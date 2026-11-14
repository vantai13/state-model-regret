/* Doan Van Tai — streaming classic Ethernet pcap -> row-major <i4 (all,s0,s1).
 * gcc -O2 -std=c99 trace_rates.c -lm -o /tmp/trace_rates
 * zcat trace.pcap.gz | /tmp/trace_rates --bin .01 --mod 1000 --out rates.bin
 * Hash: directional FNV-1a-64, offset/seed 14695981039346656037, prime
 * 1099511628211; bytes = IP version, src, dst, final protocol, network-order
 * sport,dport (zero for non-TCP/UDP). One 802.1Q tag is supported.
 * Missing tuple headers/noninitial fragments are parse errors, never sampled.
 * Snaplen-limited payloads are normal; incomplete pcap records are counted
 * separately. A partial final body counts in all, but is never sampled.
 */
#include <errno.h>
#include <inttypes.h>
#include <limits.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void die(const char *s) { fprintf(stderr, "trace_rates: %s\n", s); exit(1); }
static unsigned be16(const unsigned char *p) { return (unsigned)p[0]*256+p[1]; }
static uint32_t u32(const unsigned char *p, int le) {
    return le ? (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24
              : (uint32_t)p[3]|(uint32_t)p[2]<<8|(uint32_t)p[1]<<16|(uint32_t)p[0]<<24;
}
static uint64_t hash_bytes(uint64_t h, const unsigned char *p, size_t n) {
    while (n--) h = (h ^ *p++) * UINT64_C(1099511628211);
    return h;
}
/* Return 1=tuple, 0=non-IP, -1=unavailable/malformed tuple. */
static int tuple(const unsigned char *p, size_t n, uint64_t *hash) {
    size_t o=14, end, pos, addr, len;
    unsigned type, ver, proto;
    unsigned char key[38], ports[4]={0,0,0,0};
    if (n<14) return -1;
    type=be16(p+12);
    if (type==0x8100) {
        if (n<18) return -1;
        type=be16(p+16); o=18;
    }
    if (type==0x0800) {
        if (n<o+20 || p[o]>>4!=4) return -1;
        len=(p[o]&15)*4; end=o+be16(p+o+2);
        if (len<20 || n<o+len || end<o+len || (be16(p+o+6)&0x1fff)) return -1;
        ver=4; proto=p[o+9]; addr=o+12; pos=o+len; len=8;
    } else if (type==0x86dd) {
        if (n<o+40 || p[o]>>4!=6) return -1;
        ver=6; proto=p[o+6]; addr=o+8; pos=o+40;
        end=pos+be16(p+o+4); len=32;
        /* Walk IPv6 option/routing/fragment/AH headers within caplen. */
        while (proto==0 || proto==43 || proto==60 || proto==44 || proto==51) {
            size_t step;
            if (pos+2>n || pos+2>end) return -1;
            if (proto==44) {
                if (pos+8>n || pos+8>end || (be16(p+pos+2)&0xfff8)) return -1;
                step=8;
            } else step=(proto==51) ? (p[pos+1]+2)*4 : (p[pos+1]+1)*8;
            if (pos+step>n || pos+step>end) return -1;
            proto=p[pos]; pos+=step;
        }
    } else return 0;
    if (proto==6 || proto==17) {
        if (pos+4>n || pos+4>end) return -1;
        memcpy(ports,p+pos,4);
    }
    key[0]=(unsigned char)ver; memcpy(key+1,p+addr,len);
    key[1+len]=(unsigned char)proto; memcpy(key+2+len,ports,4);
    *hash=hash_bytes(UINT64_C(14695981039346656037),key,len+6);
    return 1;
}
static void put32(FILE *f, uint32_t x) {
    unsigned char b[4]={(unsigned char)x,(unsigned char)(x>>8),
                        (unsigned char)(x>>16),(unsigned char)(x>>24)};
    if (fwrite(b,1,4,f)!=4) die("output write failed");
}
int main(int argc, char **argv) {
    double bin=.01;
    uint64_t mod=1000, bin_ns, start=0, packets=0, errors=0, nonip=0;
    uint64_t truncated=0, snap_truncated=0, header_truncated=0, ns;
    size_t used=0, capacity=0, buffer_size=0, got, i;
    int32_t (*counts)[3]=NULL;
    unsigned char h[24], rh[16], *buffer=NULL;
    const char *out="rates.bin", *meta=NULL;
    char *meta_default;
    int le, nano, have_start=0;
    for (int a=1;a<argc;a++) {
        char *tail;
        if (a+1>=argc) die("expected --bin SECONDS --mod M --out FILE [--meta FILE]");
        if (!strcmp(argv[a],"--bin")) {
            bin=strtod(argv[++a],&tail); if (*tail) die("invalid bin");
        } else if (!strcmp(argv[a],"--mod")) {
            const char *s=argv[++a]; errno=0; mod=strtoull(s,&tail,10);
            if (errno || *s=='-' || !*s || *tail) die("invalid mod");
        } else if (!strcmp(argv[a],"--out")) out=argv[++a];
        else if (!strcmp(argv[a],"--meta")) meta=argv[++a];
        else die("unknown option");
    }
    if (!isfinite(bin) || bin<1e-9 || bin>1e9 || mod<2) die("bin must be >=1 ns and <=1e9 s; mod >=2");
    bin_ns=(uint64_t)llround(bin*1e9);
    if (fread(h,1,24,stdin)!=24) die("incomplete classic pcap header");
    le=!memcmp(h,"\xd4\xc3\xb2\xa1",4)||!memcmp(h,"\x4d\x3c\xb2\xa1",4);
    nano=!memcmp(h,"\x4d\x3c\xb2\xa1",4)||!memcmp(h,"\xa1\xb2\x3c\x4d",4);
    if (!le && memcmp(h,"\xa1\xb2\xc3\xd4",4) && !nano) die("not classic pcap");
    if ((le ? h[4]!=2||h[5]!=0||h[6]!=4||h[7]!=0 : h[4]!=0||h[5]!=2||h[6]!=0||h[7]!=4)) die("requires pcap 2.4");
    if ((u32(h+20,le)&0xffff)!=1) die("requires Ethernet linktype");
    while ((got=fread(rh,1,16,stdin))) {
        uint32_t cap, wire, frac;
        size_t idx;
        uint64_t hash;
        int status;
        if (got!=16) { errors++; header_truncated++; break; }
        cap=u32(rh+8,le); wire=u32(rh+12,le); frac=u32(rh+4,le);
        if (cap>16*1024*1024) die("caplen exceeds safety limit (16 MiB)");
        if (frac>=(nano ? 1000000000U : 1000000U)) die("invalid packet timestamp");
        ns=(uint64_t)u32(rh,le)*1000000000+frac*(nano ? 1U : 1000U);
        if (!have_start) { start=ns; have_start=1; }
        if (ns<start) die("packet timestamp precedes series origin");
        idx=(size_t)((ns-start)/bin_ns);
        if (idx>=100000000) die("series exceeds safety limit (100M bins)");
        if (idx>=capacity) {
            size_t old=capacity;
            capacity=capacity ? capacity : 1024;
            while (capacity<=idx) capacity*=2;
            void *tmp=realloc(counts,capacity*sizeof(*counts));
            if (!tmp) die("out of memory");
            counts=tmp; memset(counts+old,0,(capacity-old)*sizeof(*counts));
        }
        if (idx>=used) used=idx+1;
        if (counts[idx][0]==INT32_MAX) die("int32 bin count overflow");
        counts[idx][0]++; packets++;
        if (cap<wire) snap_truncated++;
        if (cap>buffer_size) {
            void *tmp=realloc(buffer,cap);
            if (!tmp) die("out of memory");
            buffer=tmp; buffer_size=cap;
        }
        if (cap && fread(buffer,1,cap,stdin)!=cap) { errors++; truncated++; break; }
        status=cap>wire ? -1 : tuple(buffer,cap,&hash);
        if (status<0) errors++;
        else if (!status) nonip++;
        else if (hash%mod<2) counts[idx][1+hash%mod]++;
    }
    if (ferror(stdin)) die("input read failed");
    FILE *f=fopen(out,"wb"); if (!f) die("cannot open output");
    for (i=0;i<used;i++) for (int j=0;j<3;j++) put32(f,(uint32_t)counts[i][j]);
    if (fclose(f)) die("output close failed");
    meta_default=malloc(strlen(out)+6); if (!meta_default) die("out of memory");
    sprintf(meta_default,"%s.json",out); if (!meta) meta=meta_default;
    f=fopen(meta,"w"); if (!f) die("cannot open metadata");
    fprintf(f,"{\"start_ns\":%"PRIu64",\"start_time\":%.9f,\"bin\":%.9f,"
            "\"bins\":%zu,\"packets\":%"PRIu64",\"parse_errors\":%"PRIu64","
            "\"non_ip\":%"PRIu64",\"truncated_records\":%"PRIu64","
            "\"truncated_record_headers\":%"PRIu64",\"snaplen_truncated\":%"PRIu64","
            "\"mod\":%"PRIu64",\"hash\":\"FNV-1a-64\","
            "\"hash_seed\":\"14695981039346656037\",\"format\":\"<i4 [bins,3]: all,s0,s1\"}\n",
            start,start/1e9,bin_ns/1e9,used,packets,errors,nonip,truncated,header_truncated,snap_truncated,mod);
    if (fclose(f)) die("metadata close failed");
    free(meta_default); free(buffer); free(counts);
    return 0;
}

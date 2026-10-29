// Doan Van Tai. Integer-lattice Bellman functions with measured compression error.
// Compression changes the numerical representation, never the queue dynamics.
#include <vector>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <limits>
#include <string>
#include <stdexcept>
using I=int64_t;using R=long double;
struct F{std::vector<I>x;std::vector<R>y;};
struct Pair{F f[2];R error=0;size_t peak=0;};
static thread_local std::string failure;
static R magnitude(const F&f){R m=0;for(R v:f.y)m=std::max(m,std::fabs(v));return m;}
static R value(const F&f,I q,size_t&j){
 if(q<=0)return f.y.front();if(q>=f.x.back())return 0;
 while(j+1<f.x.size()&&f.x[j+1]<=q)++j;
 R t=R(q-f.x[j])/R(f.x[j+1]-f.x[j]);return f.y[j]+t*(f.y[j+1]-f.y[j]);
}
static F compress(const F&f,R tolerance,R&loss){
 if(f.x.size()<3){loss=0;return f;}
 std::vector<size_t>keep{0};size_t start=0;
 R lo=-std::numeric_limits<R>::infinity(),hi=-lo;
 for(size_t j=1;j<f.x.size();++j){
  R dx=R(f.x[j]-f.x[start]),s=(f.y[j]-f.y[start])/dx;
  if(s<lo||s>hi){keep.push_back(j-1);start=j-1;lo=-std::numeric_limits<R>::infinity();hi=-lo;dx=R(f.x[j]-f.x[start]);}
  lo=std::max(lo,(f.y[j]-tolerance-f.y[start])/dx);
  hi=std::min(hi,(f.y[j]+tolerance-f.y[start])/dx);
 }
 if(keep.back()!=f.x.size()-1)keep.push_back(f.x.size()-1);
 F g;for(auto j:keep){g.x.push_back(f.x[j]);g.y.push_back(f.y[j]);}
 loss=0;size_t k=0;
 for(size_t j=0;j<f.x.size();++j)loss=std::max(loss,std::fabs(value(g,f.x[j],k)-f.y[j]));
 // Outward allowance covers the chord verification and floating corridor tests.
 loss+=512*std::numeric_limits<R>::epsilon()*(magnitude(f)+1);
 loss=std::nextafter(loss,std::numeric_limits<R>::infinity());return g;
}
static Pair step(const Pair&old,I a0,I a1,R p,R pe,R tol,int reward,size_t limit){
 Pair out;R loss=0,maximum=std::max(magnitude(old.f[0]),magnitude(old.f[1]));
 for(int m=0;m<2;++m){
  I a=m?a1:a0;std::vector<I>xs{0};size_t l=0,r=0;
  while(l<old.f[0].x.size()||r<old.f[1].x.size()){
   I x;
   if(r==old.f[1].x.size()||(l<old.f[0].x.size()&&old.f[0].x[l]<=old.f[1].x[r]))x=old.f[0].x[l++];
   else x=old.f[1].x[r++];
   I q=x-a;if(q>xs.back())xs.push_back(q);
  }
  if(xs.size()==1)xs.push_back(1);
  F raw;raw.x=xs;raw.y.reserve(xs.size());size_t i=0,j=0;
  for(I q:xs){I next=std::max(I(0),q+a);
   R v=p*value(old.f[m],next,i)+(1-p)*value(old.f[1-m],next,j);
   if(reward)v+=R(reward)*R(std::max(I(0),-q-a));raw.y.push_back(v);
  }
  raw.y.back()=0; // Every source and the immediate idle are exactly zero here.
  R measured=0;out.f[m]=compress(raw,tol,measured);loss=std::max(loss,measured);
  out.peak=std::max({out.peak,old.peak,raw.x.size()});
  if(out.f[m].x.size()>limit)throw std::runtime_error("piecewise knot budget exceeded");
 }
 R maxreward=R(reward)*R(std::max({I(0),-a0,-a1}));
 out.error=std::nextafter(old.error+loss+2*pe*maximum+
  1024*std::numeric_limits<R>::epsilon()*(maximum+maxreward+1),std::numeric_limits<R>::infinity());
 return out;
}
extern "C" const char* pw_error(){return failure.c_str();}
extern "C" void* pw_idle(int H,I a0,I a1,const R*p,const R*pe,const R*tol,size_t limit){
 try{Pair v;for(int m=0;m<2;++m){v.f[m].x={0,1};v.f[m].y={0,0};}
  for(int t=1;t<=H;++t)v=step(v,a0,a1,*p,*pe,*tol,t,limit);
  return new Pair(std::move(v));
 }catch(const std::exception&e){failure=e.what();return nullptr;}
}
extern "C" void* pw_create(size_t n0,const I*x0,const R*y0,size_t n1,const I*x1,const R*y1,const R*error){
 try{auto*v=new Pair;v->f[0].x.assign(x0,x0+n0);v->f[0].y.assign(y0,y0+n0);
  v->f[1].x.assign(x1,x1+n1);v->f[1].y.assign(y1,y1+n1);v->error=*error;return v;
 }catch(const std::exception&e){failure=e.what();return nullptr;}
}
extern "C" void* pw_age(void*initial,int steps,I a0,I a1,const R*p,const R*pe,const R*tol,size_t limit){
 try{Pair v=*static_cast<Pair*>(initial);for(int t=0;t<steps;++t)v=step(v,a0,a1,*p,*pe,*tol,0,limit);return new Pair(std::move(v));
 }catch(const std::exception&e){failure=e.what();return nullptr;}
}
extern "C" size_t pw_size(void*v,int mode){return static_cast<Pair*>(v)->f[mode].x.size();}
extern "C" void pw_copy(void*v,int mode,I*x,R*y){auto&f=static_cast<Pair*>(v)->f[mode];std::copy(f.x.begin(),f.x.end(),x);std::copy(f.y.begin(),f.y.end(),y);}
extern "C" void pw_meta(void*v,R*error,size_t*peak){auto*p=static_cast<Pair*>(v);*error=p->error;*peak=p->peak;}
extern "C" void pw_free(void*v){delete static_cast<Pair*>(v);}

// Doan Van Tai. Exact integer enclosures of fixed-decimal spectral point sums.
// A common infinity-norm radius bounds both complex coordinates. Truncation
// always increases the radius; powers use multiplication only.
#include <boost/multiprecision/cpp_int.hpp>
#include <cstdint>
#include <string>
#include <sstream>
#include <vector>
#include <stdexcept>
using Z=boost::multiprecision::cpp_int;
static constexpr long BITS=384;
static thread_local std::string answer;
static Z absz(const Z& x){return x<0?-x:x;}
static Z floor_shift(const Z& x,long k){
 if(k<=0)return x;
 if(x==0)return 0;
 if(k>long(boost::multiprecision::msb(absz(x)))+2)return x<0?Z(-1):Z(0);
 if(x>=0)return x>>k;
 return -((-x+(Z(1)<<k)-1)>>k);
}
static Z ceil_shift(const Z& x,long k){return -floor_shift(-x,k);}
struct Ball{Z re=0,im=0,rad=0;long exp=0;};
static bool zero(const Ball& a){return a.re==0&&a.im==0&&a.rad==0;}
static Ball normal(Ball a){
 Z mx=absz(a.re);if(absz(a.im)>mx)mx=absz(a.im);if(a.rad>mx)mx=a.rad;
 if(mx==0)return a;
 long shift=long(boost::multiprecision::msb(mx))+1-BITS;
 if(shift>0){a.re=floor_shift(a.re,shift);a.im=floor_shift(a.im,shift);a.rad=ceil_shift(a.rad,shift)+1;a.exp+=shift;}
 return a;
}
static Ball align(Ball a,long e){
 if(e>a.exp){long k=e-a.exp;a.re=floor_shift(a.re,k);a.im=floor_shift(a.im,k);a.rad=ceil_shift(a.rad,k)+1;a.exp=e;}
 return a;
}
static Ball add(Ball a,Ball b){
 if(zero(a))return b;if(zero(b))return a;
 long e=std::max(a.exp,b.exp);a=align(a,e);b=align(b,e);
 Ball c;c.re=a.re+b.re;c.im=a.im+b.im;c.rad=a.rad+b.rad;c.exp=e;return normal(c);
}
static Ball mul(const Ball& a,const Ball& b){
 Ball c;c.re=a.re*b.re-a.im*b.im;c.im=a.re*b.im+a.im*b.re;
 c.rad=(absz(a.re)+absz(a.im))*b.rad+(absz(b.re)+absz(b.im))*a.rad+2*a.rad*b.rad;
 c.exp=a.exp+b.exp;return normal(c);
}
static Ball power(Ball a,uint64_t q){
 Ball result;result.re=1;
 while(q){if(q&1)result=mul(result,a);q>>=1;if(q)a=mul(a,a);}
 return result;
}
static Z ten(unsigned n){Z result=1;for(unsigned i=0;i<n;++i)result*=10;return result;}
static Z decimal_scaled(std::string s){
 if(s.empty())throw std::runtime_error("empty decimal");
 bool negative=false;if(s[0]=='-'||s[0]=='+'){negative=s[0]=='-';s.erase(0,1);}
 int exponent=0;auto e=s.find_first_of("eE");if(e!=std::string::npos){exponent=std::stoi(s.substr(e+1));s.resize(e);}
 auto dot=s.find('.');int digits=0;if(dot!=std::string::npos){digits=s.size()-dot-1;s.erase(dot,1);}
 if(std::abs(exponent-digits)>10000)throw std::runtime_error("decimal exponent budget");
 Z num=0;for(char c:s){if(c<'0'||c>'9')throw std::runtime_error("invalid decimal");num=10*num+c-'0';}
 Z den=1;if(exponent>=digits)num*=ten(exponent-digits);else den=ten(digits-exponent);
 num<<=BITS;if(negative)num=-num;
 if(num>=0)return num/den;
 return -((-num+den-1)/den);
}
static Ball parse(const char* re,const char* im){
 Ball a;a.re=decimal_scaled(re);a.im=decimal_scaled(im);a.rad=1;a.exp=-BITS;return normal(a);
}
static void emit(std::ostringstream& out,const Ball& a){
 out<<"[\""<<a.re<<"\",\""<<a.im<<"\",\""<<a.rad<<"\","<<a.exp<<']';
}
extern "C" const char* spectral_points(size_t n,const char** fields,size_t count,const uint64_t* qs,const char** initial){
 try{
  if(n==0||n>20000||count>10000)throw std::runtime_error("evaluation size budget");
  std::vector<Ball> roots(n),off(n),on(n);
  for(size_t i=0;i<n;++i){roots[i]=parse(fields[6*i],fields[6*i+1]);off[i]=parse(fields[6*i+2],fields[6*i+3]);on[i]=parse(fields[6*i+4],fields[6*i+5]);}
  Ball z0=parse(initial[0],initial[1]),z1=parse(initial[2],initial[3]);
  std::ostringstream out;out<<"{\"bits\":"<<BITS<<",\"points\":[";
  for(size_t j=0;j<count;++j){
   if(qs[j]>(uint64_t(1)<<40))throw std::runtime_error("power exponent budget");
   Ball a,b;if(qs[j]==0){a=z0;b=z1;}else for(size_t i=0;i<n;++i){Ball p=power(roots[i],qs[j]);a=add(a,mul(off[i],p));b=add(b,mul(on[i],p));}
   if(j)out<<',';out<<'[';emit(out,a);out<<',';emit(out,b);out<<']';
  }
  out<<"]}";answer=out.str();return answer.c_str();
 }catch(const std::exception& e){answer="{\"error\":\""+std::string(e.what())+"\"}";return answer.c_str();}
}

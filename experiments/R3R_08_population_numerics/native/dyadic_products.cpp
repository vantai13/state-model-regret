// Doan Van Tai. Exact-integer outward complex boxes with a shared binary scale.
// Re/Im center and a common infinity-norm radius are dyadic integers. Every
// multiplication/rounding enclosure uses cpp_int, not an assumed libm error.
#include <boost/multiprecision/cpp_int.hpp>
#include <vector>
#include <string>
#include <sstream>
#include <stdexcept>
using boost::multiprecision::cpp_int;using Z=cpp_int;
static const int BITS=384;
static thread_local std::string answer;
static Z absz(const Z&x){return x<0?-x:x;}
static Z floor_shift(const Z&x,unsigned k){if(x>=0)return x>>k;Z a=-x;return -((a+(Z(1)<<k)-1)>>k);}
static Z ceil_shift(const Z&x,unsigned k){return -floor_shift(-x,k);}
struct Ball{Z re=0,im=0,rad=0;long exp=0;};
static Ball normal(Ball x){
 Z mx=absz(x.re);if(absz(x.im)>mx)mx=absz(x.im);if(x.rad>mx)mx=x.rad;
 if(mx==0)return x;
 long shift=long(boost::multiprecision::msb(mx))+1-BITS;
 if(shift>0){x.re=floor_shift(x.re,shift);x.im=floor_shift(x.im,shift);x.rad=ceil_shift(x.rad,shift)+1;x.exp+=shift;}
 return x;
}
static Ball mul(const Ball&a,const Ball&b){
 Ball c;c.re=a.re*b.re-a.im*b.im;c.im=a.re*b.im+a.im*b.re;
 c.rad=(absz(a.re)+absz(a.im))*b.rad+(absz(b.re)+absz(b.im))*a.rad+2*a.rad*b.rad;
 c.exp=a.exp+b.exp;return normal(std::move(c));
}
static Z ten(unsigned n){Z v=1;for(unsigned i=0;i<n;++i)v*=10;return v;}
static Z decimal_scaled(std::string s){
 bool neg=false;if(s[0]=='-'||s[0]=='+'){neg=s[0]=='-';s.erase(0,1);}
 int exponent=0;auto e=s.find_first_of("eE");if(e!=std::string::npos){exponent=std::stoi(s.substr(e+1));s.resize(e);}
 auto dot=s.find('.');int digits=0;if(dot!=std::string::npos){digits=s.size()-dot-1;s.erase(dot,1);}
 if(std::abs(exponent-digits)>10000)throw std::runtime_error("decimal exponent budget");
 Z numerator=0;for(char c:s){if(c<'0'||c>'9')throw std::runtime_error("invalid decimal root");numerator=10*numerator+(c-'0');}
 Z denominator=1;if(exponent>=digits)numerator*=ten(exponent-digits);else denominator=ten(digits-exponent);
 numerator<<=BITS;if(neg)numerator=-numerator;
 if(numerator>=0)return numerator/denominator;
 return -((-numerator+denominator-1)/denominator);
}
struct Product{
 std::vector<Ball>levels;std::vector<bool>used;
 void add(Ball x){size_t i=0;while(i<levels.size()&&used[i]){x=mul(levels[i],x);used[i]=false;++i;}
  if(i==levels.size()){levels.push_back(std::move(x));used.push_back(true);}else{levels[i]=std::move(x);used[i]=true;}}
 Ball value(){Ball x;x.re=1;for(size_t i=levels.size();i-->0;)if(used[i])x=mul(x,levels[i]);return x;}
};
extern "C" const char* dyadic_derivatives(size_t n,const char**real,const char**imag){
 try{
  if(n==0||n>20000)throw std::runtime_error("root count budget");
  std::vector<Ball>roots(n);std::vector<Product>products(n);
  for(size_t i=0;i<n;++i){roots[i].re=decimal_scaled(real[i]);roots[i].im=decimal_scaled(imag[i]);roots[i].rad=1;roots[i].exp=-BITS;}
  for(size_t i=0;i<n;++i)for(size_t j=0;j<i;++j){Ball d;
   d.re=roots[i].re-roots[j].re;d.im=roots[i].im-roots[j].im;d.rad=2;d.exp=-BITS;
   if(absz(d.re)<=d.rad&&absz(d.im)<=d.rad)throw std::runtime_error("distinct roots not certified");
   products[i].add(d);d.re=-d.re;d.im=-d.im;products[j].add(std::move(d));
  }
  std::ostringstream out;out<<"{\"bits\":"<<BITS<<",\"products\":[";
  for(size_t i=0;i<n;++i){auto d=products[i].value();if(i)out<<',';
   out<<"[\""<<d.re<<"\",\""<<d.im<<"\",\""<<d.rad<<"\","<<d.exp<<']';}
  out<<"]}";answer=out.str();return answer.c_str();
 }catch(const std::exception&e){answer="{\"error\":\""+std::string(e.what())+"\"}";return answer.c_str();}
}

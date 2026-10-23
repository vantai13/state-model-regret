// Doan Van Tai: finite-horizon idle DP. Above t*max_drain value is exactly zero.
#include <vector>
#include <algorithm>
#include <cstdint>
template<class T> void solve(int H,int a0,int a1,T p,int count,const int64_t* indices,T* out){
 int drain=std::max({0,-a0,-a1});int N=H*drain;
 std::vector<T> old(2*(N+1),0),next(2*(N+1),0);int prev=0;
 for(int t=1;t<=H;++t){
  int stop=t*drain;
  for(int q=0;q<=stop;++q){
   int q0=std::max(0,q+a0),q1=std::max(0,q+a1);
   T v00=q0<=prev?old[2*q0]:0,v01=q0<=prev?old[2*q0+1]:0;
   T v10=q1<=prev?old[2*q1]:0,v11=q1<=prev?old[2*q1+1]:0;
   next[2*q]=T(t)*T(std::max(0,-q-a0))+p*v00+(T(1)-p)*v01;
   next[2*q+1]=T(t)*T(std::max(0,-q-a1))+(T(1)-p)*v10+p*v11;
  }
  old.swap(next);prev=stop;
 }
 for(int k=0;k<count;++k){int64_t i=indices[k];out[2*k]=i<=N?old[2*i]:0;out[2*k+1]=i<=N?old[2*i+1]:0;}
}
extern "C" void idle64(int H,int a,int b,const double* p,int count,const int64_t* indices,double* out){solve(H,a,b,*p,count,indices,out);}
extern "C" void idle80(int H,int a,int b,const long double* p,int count,const int64_t* indices,long double* out){solve(H,a,b,*p,count,indices,out);}

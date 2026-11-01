#include <vector>
#include <cassert>
int f(const std::vector<int>& a,int t){int l=0,r=(int)a.size()-1;while(l<=r){int m=(l+r)/2;if(a[m]==t)return m;if(a[m]<t)l=m+1;else r=m-1;}return -1;}
int main(){assert(f({1,3,5},5)==2);assert(f({},1)==-1);assert(f({1},1)==0);}

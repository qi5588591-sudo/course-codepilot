#include <cstdlib>
#include <cassert>
int f(int a,int b){a=std::abs(a);b=std::abs(b);while(b){int c=a%b;a=b;b=c;}return a;}
int main(){assert(f(-12,18)==6);assert(f(0,0)==0);assert(f(7,0)==7);}

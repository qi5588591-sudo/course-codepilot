#include <string>
#include <algorithm>
#include <cctype>
#include <cassert>
bool f(std::string s){std::string a;for(unsigned char c:s)if(std::isalnum(c))a+=std::tolower(c);std::string b=a;std::reverse(b.begin(),b.end());return a==b;}
int main(){assert(f("A man, a plan, a canal: Panama"));assert(!f("abc"));assert(f(""));}

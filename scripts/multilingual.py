"""Compile/run nine trusted reference examples. This is NOT an LLM benchmark."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
data={
'javascript':[
('binary_search', 'function f(a,t){let l=0,r=a.length-1;while(l<=r){let m=(l+r)>>1;if(a[m]===t)return m;if(a[m]<t)l=m+1;else r=m-1;}return -1;}\nif(f([1,3,5],5)!==2||f([],1)!==-1||f([1],1)!==0)throw Error("failed");'),
('gcd', 'function f(a,b){a=Math.abs(a);b=Math.abs(b);while(b){[a,b]=[b,a%b];}return a;}\nif(f(-12,18)!==6||f(0,0)!==0||f(7,0)!==7)throw Error("failed");'),
('palindrome', 'function f(s){s=s.toLowerCase().replace(/[^a-z0-9]/g,"");return s===s.split("").reverse().join("");}\nif(!f("A man, a plan, a canal: Panama")||f("abc")||!f(""))throw Error("failed");')],
'java':[
('binary_search','class Main { static int f(int[] a,int t){int l=0,r=a.length-1;while(l<=r){int m=(l+r)/2;if(a[m]==t)return m;if(a[m]<t)l=m+1;else r=m-1;}return -1;} public static void main(String[] args){if(f(new int[]{1,3,5},5)!=2||f(new int[]{},1)!=-1||f(new int[]{1},1)!=0)throw new AssertionError();}}'),
('gcd','class Main { static int f(int a,int b){a=Math.abs(a);b=Math.abs(b);while(b!=0){int c=a%b;a=b;b=c;}return a;} public static void main(String[] args){if(f(-12,18)!=6||f(0,0)!=0||f(7,0)!=7)throw new AssertionError();}}'),
('palindrome','class Main { static boolean f(String s){s=s.toLowerCase().replaceAll("[^a-z0-9]","");return s.equals(new StringBuilder(s).reverse().toString());} public static void main(String[] args){if(!f("A man, a plan, a canal: Panama")||f("abc")||!f(""))throw new AssertionError();}}')],
'cpp':[
('binary_search','#include <vector>\n#include <cassert>\nint f(const std::vector<int>& a,int t){int l=0,r=(int)a.size()-1;while(l<=r){int m=(l+r)/2;if(a[m]==t)return m;if(a[m]<t)l=m+1;else r=m-1;}return -1;}\nint main(){assert(f({1,3,5},5)==2);assert(f({},1)==-1);assert(f({1},1)==0);}'),
('gcd','#include <cstdlib>\n#include <cassert>\nint f(int a,int b){a=std::abs(a);b=std::abs(b);while(b){int c=a%b;a=b;b=c;}return a;}\nint main(){assert(f(-12,18)==6);assert(f(0,0)==0);assert(f(7,0)==7);}'),
('palindrome','#include <string>\n#include <algorithm>\n#include <cctype>\n#include <cassert>\nbool f(std::string s){std::string a;for(unsigned char c:s)if(std::isalnum(c))a+=std::tolower(c);std::string b=a;std::reverse(b.begin(),b.end());return a==b;}\nint main(){assert(f("A man, a plan, a canal: Panama"));assert(!f("abc"));assert(f(""));}')]
}
results=[]
for language,cases in data.items():
    for name,code in cases:
        destination=root/'examples'/language/name
        destination.mkdir(parents=True,exist_ok=True)
        filename={'javascript':'main.js','java':'Main.java','cpp':'main.cpp'}[language]
        (destination/filename).write_text(code+'\n',encoding='utf-8')
        row={'language':language,'case':name,'type':'trusted_reference_smoke','status':'not_run'}
        compiler={'javascript':'node','java':'javac','cpp':'g++'}[language]
        if not shutil.which(compiler): row['reason']='toolchain not found'
        else:
            with tempfile.TemporaryDirectory(prefix='codepilot-smoke-') as tmp:
                source=Path(tmp)/filename;source.write_text(code,encoding='utf-8')
                commands={'javascript':[['node',str(source)]],
                          'java':[['javac',str(source)],['java','-cp',tmp,'Main']],
                          'cpp':[['g++','-std=c++17',str(source),'-o',str(Path(tmp)/'main.exe')],[str(Path(tmp)/'main.exe')]]}[language]
                row['commands']=commands
                row['status']='passed'
                try:
                    for command in commands:
                        process=subprocess.run(command,capture_output=True,text=True,errors='replace',timeout=45)
                        if process.returncode:
                            row.update(status='failed',exit_code=process.returncode,output=(process.stdout+process.stderr)[-4000:]);break
                except (OSError,subprocess.TimeoutExpired) as exc:row.update(status='failed',output=str(exc))
        results.append(row)
        print(language,name,row['status'])
(root/'artifacts').mkdir(exist_ok=True)
(root/'artifacts/multilingual-smoke.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')

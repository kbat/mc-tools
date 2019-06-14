#include <iostream>
#include <fstream>
#include <cstdlib>
#include <vector>
#include <numeric>

// od -t dI -N 16 /home/kbat/figs/toy-moderator/ptrac
// bless, hd - other viewers

using namespace std;

vector<char> fortranRead(ifstream &f)
{
  vector<char> vec;

  int beg;
  f.read(reinterpret_cast<char*>(&beg), sizeof(beg));
  if (beg==0)
    return vec;

  cout << "\t === " << beg << " bytes to read" << endl;
  
  vec.resize(beg);
  f.read(&vec.front(), beg);
  
  //  cout << int(vec[0]) << endl;

  int end;
  
  f.read(reinterpret_cast<char*>(&end), sizeof(end));
  if (beg!=end) {
    cerr << "Format error" << endl;
    f.close();
    exit(1);
  }
  return vec;
}

int main(int argc, const char **argv)
{
  ifstream f;
  f.open(argv[1], ios::in|ios::binary);

  if (f.is_open())
    {
      int tmp = int(fortranRead(f)[0]); cout << tmp << endl;
      vector<char> vtmp = fortranRead(f);
      vector<char>::iterator p1, p2;
      p1 = vtmp.begin();
      p2 = p1 + 8;
      string kod = accumulate(p1, p2, string(""));
      p1 = p2;  p2 += 5;
      string ver = accumulate(p1, p2, string(""));
      p1 = p2;  p2 += 30;
      string loddat = accumulate(p1, p2, string(""));
      p1 = p2;  p2 = vtmp.end();
      string idtm  = accumulate(p1, p2, string(""));

      cout << "kod: " << kod << endl;
      cout << "ver: " << ver << endl;
      cout << "loddat: " << loddat << endl;
      cout << "idtm: " << idtm << endl;

      vtmp = fortranRead(f);
      p1 = vtmp.begin();
      p2 = vtmp.end();
      string aid = accumulate(p1, p2, string(""));
      cout << "aid: " << aid << endl;

      vtmp = fortranRead(f);
      cout << "number of PTRACK keywords: " << int(vtmp[0]) << endl;
      cout << "number of entries for ith keyword: " << int(vtmp[1]) << endl;

      vtmp = fortranRead(f);
    }

  
  f.close();

  return 0;
}

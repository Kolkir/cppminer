template<typename T>
class Math {
  public:
    T Add(T a, T b) {
        return AddImpl(a,b);
    }

    T Sub(T a, T b) {
        return AddImpl(a,b);
    }
  private:
    T AddImpl(T a, T b) {
        return a + b;
    }

    T SubImpl(T a, T b) {
        return a - b;
    }
};

class Base {
  public:
     virtual ~Base() { --x; }
     virtual void Print() = 0;
     virtual void Draw();
     friend bool operator==(const Derived& a, const Derived& b);

  private:
    int x = 0;
    int y = 8;
};

void Base::Draw() {
    x = x + y;
}

class Derived : public Base {
 public:
   void Print() override {
    Draw();
   }

  void operator()() {
    Print();
  }
};

bool operator==(const Base& a, const Base& b) {
    return (a.x == b.x) && (a.y == b.y);
}


int func(float x, float y){
    Math<float> m;
    return static_cast<int>(m.Add(x, y));
}

int func_TestAll(float x, float y){
    Math<float> m;
    return static_cast<int>(m.Add(x, y));
}

template<typename T>
T subtract(T&& x, T&& y){
    return x - y;
}

int maxof(int n_args, ...) {
    ++n_args;
}

template<typename T>
T adder(T v) {
  return v;
}

template<typename T, typename... Args>
T adder(T first, Args... args) {
  return first + adder(args...);
}

int main(int argc, char* argv[]) {
    auto r = subtract(4, 5);
    auto s = func(3.4, 5.8);
    return r+s;
}

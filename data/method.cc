class Base {
  public:
     virtual void Draw();
  private:
    int x = 0;
    int y = 8;
};

void Base::Draw() {
    x = x + y;
}

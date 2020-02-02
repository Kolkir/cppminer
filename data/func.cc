int div(int x, int y) {
    float z = 45;
    if (y != 0) {
        return x /y;
    } else {
        return 0;
    }
}

int main() {
    auto e = 8;
    auto r = div(5, e);
    return r;
}

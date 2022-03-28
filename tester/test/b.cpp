#include <iostream>
int main(int argc, char **argv) {
    int a;
    std::cin>>a;
    std::cout<<"Yes!\nDPC++ is good!\n";
    if (argc > 1) {
        for (int i = 1; i < argc; i++)
            std::cout << "Argument " << i << ": " << argv[i] << std::endl;
    }
   return 0;
}

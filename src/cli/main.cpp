#include <iostream>

int main(int argc, char** argv) {
    std::cout << "Casino Odds & Prediction Engine (skeleton build)\n";
    std::cout << "Number of args: " << argc << "\n";
    if (argc > 1) {
        std::cout << "First arg: " << argv[1] << "\n";
    }
    return 0;
}

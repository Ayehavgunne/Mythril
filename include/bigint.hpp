/*
    BigInt Library for C++

    MIT License
    
    Copyright (c) 2024 Samuel Herts
    
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    
    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.
    
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
*/

#ifndef BIGINT_H_
#define BIGINT_H_

#include <string>
#include <sstream>
#include <utility>
#include <vector>
#include <cmath>
#include <limits>
#include <stdexcept>
#include <iostream>
#include <functional>
#include <algorithm>
#include <random>
#include <iomanip>

namespace BigInt {
    class bigint
    {
    public:
        //                   LLONG_MAX = 9'223'372'036'854'775'807
        static constexpr auto MAX_SIZE = 1000000000LL;

        bigint() : vec({0}) {}

        bigint(const std::string& s) {
            if (!is_bigint(s)) { throw std::runtime_error("Invalid Big Integer."); }
            if (s[0] == '-') {
                *this = bigint(s.substr(1));
                if (*this == 0)
                    throw std::runtime_error("Invalid Big Integer.");
                is_neg = true;
            }
            else if (s[0] == '0' && s[1] == 'x') {
                // Hex string
                is_neg = false;
                vec = hex_to_vector(s);
            }
            else {
                is_neg = false;
                vec = string_to_vector(s);
            }
        }

        bigint(const char c) {
            if (const int temp = static_cast<unsigned char>(c); isdigit(temp)) {
                *this = bigint(char_to_int(c));
            }
            else {
                throw std::runtime_error("Invalid Big Integer has been fed.");
            }
        }

        bigint(const char* n) : bigint(std::string(n)) {}

        bigint(const int n) :           bigint(static_cast<long long>(n)) {}
        bigint(const unsigned int n) :  bigint(static_cast<long long>(n)) {}
        bigint(const long n) :          bigint(static_cast<long long>(n)) {}
        bigint(const unsigned long n) : bigint(static_cast<long long>(n)) {}
        bigint(const double n) :        bigint(static_cast<long long>(n)) {}

        bigint(const long long n): is_neg(n < 0) {
            if (n == 0) {
                is_neg = false;
                vec.push_back(0);
                return;
            }
            unsigned long long val = n;
            if (is_neg) {
                val = 0ULL - val;
            }
            vec.reserve(2);

            while (val > 0) {
                vec.emplace_back(val % MAX_SIZE);
                val /= MAX_SIZE;
            }
            std::reverse(vec.begin(), vec.end());
        }

        bigint(unsigned long long n) {
            if (n >= MAX_SIZE) {
                vec.emplace_back(n / MAX_SIZE);
                vec.emplace_back(n % MAX_SIZE);
            }
            else {
                vec.emplace_back(n);
            }
        }

        bigint(const bigint& n) = default;

        /* If initializing from a vector that should be negative, the negative value must be set afterward.
         * bigint alpha(std::vector(...));
         * -alpha;
         */
        bigint(std::vector<long long> n) : vec(std::move(n)) {}

        bigint& operator=(const bigint& other) {
            if (this == &other)
                return *this;
            this->is_neg = other.is_neg;
            this->vec = other.vec;

            return *this;
        }

        explicit operator int() const {
            return static_cast<int>(vec.back());
        }

        explicit operator long long() const {
            return vec.back();
        }

        explicit operator std::string() const {
            return (this->is_neg ? "-" : "") + vector_to_string(this->vec);
        }

        friend std::ostream& operator<<(std::ostream& stream, const bigint& n) {
            stream << std::string(n);
            return stream;
        }

        bigint operator+=(const bigint& rhs) {
            if (*this == 0 && rhs == 0) return *this;
            if (*this == 0) {
                *this = rhs;
                return *this;
            }
            if (rhs != 0) {
                *this = add(*this, rhs);
            }
            return *this;
        }

        bigint operator+(const bigint& rhs) const {
            bigint result = *this;
            result += rhs;
            return result;
        }

        bigint operator-=(const bigint& rhs) {
            if (rhs == 0) { return *this; }
            if (*this == rhs) {
                *this = 0;
                return *this;
            }
            *this = subtract(*this, rhs);
            return *this;
        }

        bigint operator-(const bigint& rhs) const {
            bigint result = *this;
            result -= rhs;
            return result;
        }

        bigint operator*=(const bigint& rhs) {
            *this = multiply(*this, rhs);
            return *this;
        }

        bigint operator*(const bigint& rhs) const {
            bigint result = *this;
            result *= rhs;
            return result;
        }

        bigint& operator/=(const bigint& rhs) {
            *this = divide(*this, rhs);
            return *this;
        }

        bigint operator/(const bigint& rhs) const {
            bigint result = *this;
            result /= rhs;
            return result;
        }

        bigint operator%=(const bigint& rhs) {
            *this = mod(*this, rhs);
            return *this;
        }

        bigint operator%(const bigint& rhs) const {
            bigint result = *this;
            result %= rhs;
            return result;
        }

        bigint operator++() {
            *this += 1;
            return *this;
        }

        bigint operator++(int) {
            bigint tmp(*this);
            operator++();
            return tmp;
        }

        bigint operator--() {
            *this -= 1;
            return *this;
        }

        bigint operator--(int) {
            bigint tmp(*this);
            operator--();
            return tmp;
        }

        bigint operator-() const & {
            bigint temp = *this;
            if (temp == 0) return temp;
            temp.is_neg = !this->is_neg;
            return temp;
        }

        bigint operator-() && {
            if (*this == 0) return *this;
            this->is_neg = !this->is_neg;
            return *this;
        }

        friend bool operator==(const bigint& l, const bigint& r) {
            if (l.is_neg != r.is_neg) {
                return false;
            }
            return l.vec == r.vec;
        }

        friend bool operator!=(const bigint& l, const bigint& r) {
            return !(l == r);
        }

        friend bool operator<(const bigint& lhs, const bigint& rhs) {
            return less_than(lhs, rhs);
        }

        friend bool operator>(const bigint& l, const bigint& r) {
            return r < l;
        }

        friend bool operator<=(const bigint& l, const bigint& r) {
            return r >= l;
        }

        friend bool operator>=(const bigint& l, const bigint& r) {
            return !(l < r);
        }

        explicit operator bool() const {
            return !(vec.size() == 1 && vec.front() == 0);
        }

        friend std::hash<bigint>;

        static bigint pow(const bigint& base, const bigint& exponent) {
            if (base == 0) return 0;
            if (base == 1) return 1;
            if (exponent < 0) return 0;
            if (exponent == 0) return 1;
            if (exponent == 1) return base;
            if (base == 10) return pow10(exponent);

            const bigint tmp = pow(base, exponent / 2);
            if (exponent % 2 == 0) { return tmp * tmp; }
            return base * tmp * tmp;
        }

        static bigint pow10(const bigint& exponent) {
            if (exponent < 0) return 0;
            if (exponent == 0) return 1;
            if (exponent == 1) return 10;
            std::string result(static_cast<int>(exponent) + 1, '0');
            result[0] = '1';
            return result;
        }

        static bigint maximum(const bigint& lhs, const bigint& rhs) {
            return lhs > rhs ? lhs : rhs;
        }

        static bigint minimum(const bigint& lhs, const bigint& rhs) {
            return lhs > rhs ? rhs : lhs;
        }

        static bigint abs(const bigint& s) {
            if (!is_negative(s)) return s;

            bigint temp = s;
            temp.is_neg = false;

            return temp;
        }

        static bigint abs(bigint&& s) {
            s.is_neg = false;
            return s;
        }

        static bigint sqrt(const bigint&);

        static bigint log2(const bigint&);

        static bigint log10(const bigint&);

        static bigint logwithbase(const bigint&, const bigint&);

        static bigint antilog2(const bigint&);

        static bigint antilog10(const bigint&);

        static void swap(bigint&, bigint&);

        static bigint gcd(const bigint&, const bigint&);

        static bigint lcm(const bigint& lhs, const bigint& rhs) {
            return (lhs * rhs) / gcd(lhs, rhs);
        }

        static bigint factorial(const bigint&);

        static bool is_even(const bigint& input) {
            return !(input.vec.back() & 1);
        }

        static bool is_negative(const bigint& input) {
            return input.is_neg;
        }

        static bool is_prime(const bigint&);

        static int count_digits(const bigint&);

        static bigint sum_of_digits(const bigint& input) {
            bigint sum;
            for (auto base : input.vec) {
                for (sum = 0; base > 0; sum += base % 10, base /= 10);
            }
            return sum;
        }

        /**
         * @brief Generates a random positive bigint of a specified length.
         *
         * This method ensures the resulting bigint is valid by using a random device
         * and engine for non-deterministic seeding.
         *
         * @param length The number of digits the generated bigint should have.
         * @return A bigint object representing the randomly generated number.
         */
        static bigint random(size_t length);

    private:
        bool is_neg{false};
        std::vector<long long> vec;

        // Function Definitions for Internal Uses
        static bigint trim(bigint input) {
            while (input.vec.size() > 1 && input.vec.front() == 0) {
                input.vec.erase(input.vec.begin());
            }
            if (input.vec.empty()) {
                input.vec.push_back(0);
                input.is_neg = false;
            }
            return input;
        }

        static std::vector<long long> string_to_vector(std::string input);
        static std::vector<long long> hex_to_vector(std::string input);

        static std::string vector_to_string(const std::vector<long long>& input);

        static bigint add(const bigint&, const bigint&);

        static bigint subtract(const bigint&, const bigint&);

        static bigint multiply(const bigint&, const bigint&);

        static bigint divide(const bigint&, const bigint&);

        static bigint mod(const bigint& lhs, const bigint& rhs) {
            if (rhs == 0) { throw std::domain_error("Attempted to modulo by zero."); }
            if (lhs < rhs) {
                return lhs;
            }
            if (lhs == rhs) {
                return 0;
            }

            if (rhs == 2) {
                return !is_even(lhs);
            }

            return lhs - ((lhs / rhs) * rhs);
        }

        static bool is_bigint(const std::string&);


        static int char_to_int(const char input) {
            return input - '0';
        }

        static int int_to_char(const int input) {
            return input + '0';
        }

        static bigint negate(const bigint& input) {
            bigint temp = input;
            temp.is_neg = !temp.is_neg;
            return temp;
        }

        static bigint negate(bigint&& input) {
            input.is_neg = !input.is_neg;
            return input;
        }

        static bool less_than(const bigint& lhs, const bigint& rhs) {
            if (is_negative(lhs) && is_negative(rhs)) {
                return less_than(abs(rhs), abs(lhs));
            }

            if (is_negative(lhs) || is_negative(rhs)) {
                return is_negative(lhs);
            }

            if (lhs.vec.size() == rhs.vec.size()) {
                return lhs.vec < rhs.vec;
            }

            return lhs.vec.size() < rhs.vec.size();
        }
    };

    inline bool bigint::is_bigint(const std::string& s) {
        if (s.empty())
            return false;

        // Check for leading negative sign
        if (s[0] == '-') {
            if (s.length() == 1) return false;
            // Recursively validate the rest as a positive bigint
            // Note: leading zeros check still applies to the magnitude
            return is_bigint(s.substr(1));
        }

        // Check for hex string "0x..."
        if (s.length() > 2 && s[0] == '0' && s[1] == 'x') {
            return s.find_first_not_of("0123456789abcdefABCDEF", 2) == std::string::npos;
        }

        // Reject leading zeros for decimal numbers
        if (s.length() > 1 && s[0] == '0')
            return false;

        return s.find_first_not_of("0123456789", 0) == std::string::npos;
    }

    inline bigint bigint::add(const bigint& lhs, const bigint& rhs) {
        bool negate_answer = false;
        // Ensure both are positive
        if (is_negative(lhs) && is_negative(rhs)) negate_answer = true;
        else if (is_negative(lhs)) return subtract(rhs, abs(lhs));
        else if (is_negative(rhs)) return subtract(lhs, abs(rhs));

        // Ensure LHS is larger than RHS
        if (lhs.vec.size() < rhs.vec.size()) return add(rhs, lhs);

        // Prepare result vector with enough space (max size + 1 for potential carry)
        std::vector<long long> result;
        result.reserve(lhs.vec.size() + 1);

        long long carry = 0;
        auto it_l = lhs.vec.rbegin();
        auto it_r = rhs.vec.rbegin();

        while (it_l != lhs.vec.rend()) {
            long long sum = *it_l + carry;
            if (it_r != rhs.vec.rend()) {
                sum += *it_r;
                ++it_r;
            }

            if (sum >= MAX_SIZE) {
                sum -= MAX_SIZE;
                carry = 1;
            }
            else {
                carry = 0;
            }

            result.push_back(sum);
            ++it_l;
        }

        if (carry > 0) {
            result.push_back(carry);
        }

        std::reverse(result.begin(), result.end());
        bigint result_bigint{std::move(result)};
        return negate_answer ? negate(result_bigint) : result_bigint;
    }

    inline bigint bigint::subtract(const bigint& lhs, const bigint& rhs) {
        // Ensure LHS is larger than RHS, and both are positive
        // (-A) - (-B) == B - A
        if (is_negative(lhs) && is_negative(rhs)) {
            return subtract(abs(rhs), abs(lhs));
        }
        // (A) - (-B) == A + B
        if (is_negative(rhs)) {
            return add(lhs, abs(rhs));
        }
        // (-A) - (B) == -(A + B)
        if (is_negative(lhs)) {
            return negate(add(abs(lhs), rhs));
        }
        if (lhs < rhs) {
            return negate(subtract(rhs, lhs));
        }

        std::vector<long long> result;
        result.reserve(lhs.vec.size());
        long long borrow = 0;

        auto it_l = lhs.vec.rbegin();
        auto it_r = rhs.vec.rbegin();

        while (it_l != lhs.vec.rend()) {
            const long long l_val = *it_l;
            const long long r_val = (it_r != rhs.vec.rend()) ? *it_r : 0;

            long long diff = l_val - r_val - borrow;
            if (diff < 0) {
                diff += MAX_SIZE;
                borrow = 1;
            }
            else {
                borrow = 0;
            }
            result.push_back(diff);

            ++it_l;
            if (it_r != rhs.vec.rend()) ++it_r;
        }
        std::reverse(result.begin(), result.end());
        return trim(bigint(std::move(result)));
    }

    inline bigint bigint::multiply(const bigint& lhs, const bigint& rhs) {
        if (lhs == 0 || rhs == 0) return 0;
        if (lhs == 1) return rhs;
        if (rhs == 1) return lhs;

        if (is_negative(lhs) && is_negative(rhs)) {
            return (abs(lhs) * abs(rhs));
        }
        if (is_negative(lhs) || is_negative(rhs)) {
            return negate(abs(lhs) * abs(rhs));
        }
        if (lhs < rhs) {
            return multiply(rhs, lhs);
        }

        std::vector<long long> result(lhs.vec.size() + rhs.vec.size(), 0);

        for (auto it_lhs = lhs.vec.rbegin(); it_lhs != lhs.vec.rend(); ++it_lhs) {
            for (auto it_rhs = rhs.vec.rbegin(); it_rhs != rhs.vec.rend(); ++it_rhs) {
                // Calculate the product and the corresponding indices in the result vector
                long long mul = (*it_lhs) * (*it_rhs);
                auto pos_low_it = result.rbegin() + (std::distance(lhs.vec.rbegin(), it_lhs) + std::distance(
                                                         rhs.vec.rbegin(), it_rhs));
                auto pos_high_it = pos_low_it + 1;

                // Add the product to the result vector
                *pos_low_it += mul % MAX_SIZE;
                if (pos_high_it != result.rend()) {
                    *pos_high_it += mul / MAX_SIZE;
                }

                // Handle carry
                if (*pos_low_it >= MAX_SIZE) {
                    if (pos_high_it != result.rend()) {
                        *pos_high_it += *pos_low_it / MAX_SIZE;
                    }
                    *pos_low_it %= MAX_SIZE;
                }
            }
        }

        // Handle carries for remaining positions
        for (auto r_iter = result.rbegin(); r_iter != result.rend() - 1; ++r_iter) {
            if (*r_iter >= MAX_SIZE) {
                *(r_iter + 1) += *r_iter / MAX_SIZE;
                *r_iter %= MAX_SIZE;
            }
        }

        return trim(result);
    }


    inline bigint bigint::divide(const bigint& numerator, const bigint& denominator) {
        if (denominator == 0) {
            throw std::domain_error("Attempted to divide by zero.");
        }
        if (numerator == denominator) return 1;
        if (denominator == 1) return numerator;
        if (numerator == 0) return 0;

        if (is_negative(numerator) && is_negative(denominator)) {
            return divide(abs(numerator), abs(denominator));
        }
        if (is_negative(numerator) || is_negative(denominator)) {
            return negate(divide(abs(numerator), abs(denominator)));
        }
        if (numerator < denominator) {
            return 0;
        }
        if (numerator.vec.size() <= 1) {
            return numerator.vec.back() / denominator.vec.back();
        }

        bigint remainder = numerator;
        bigint quotient = 0;

        while (remainder >= denominator) {
            int count = count_digits(remainder) - count_digits(denominator) - 1;

            // Prevent negative exponents which cause pow() to return 0
            if (count < 0) {
                count = 0;
            }

            bigint numerator_size = pow(10, count);
            bigint temp = denominator * numerator_size;

            // Repeatedly subtract the chunk from the remainder
            while (remainder >= temp) {
                remainder -= temp;
                quotient += numerator_size;
            }
        }

        return quotient;
    }

    inline bigint bigint::sqrt(const bigint& input) {
        if (is_negative(input))
            throw std::domain_error("Square root of a negative number is complex");

        if (input == 0 || input == 1)
            return input;

        bigint oom = log10(input / 2);
        oom /= 2;
        bigint low_end = pow(10, (oom));
        bigint high_end = pow(10, (oom) + 2);
        bigint mid_point, square, answer;
        while (low_end <= high_end) {
            mid_point = (low_end + high_end) / 2;
            square = mid_point * mid_point;
            if (square == input)
                return mid_point;

            if (square < input) {
                low_end = mid_point + 1;
                answer = mid_point;
            }
            else {
                high_end = mid_point - 1;
            }
        }
        return answer;
    }

    inline bigint bigint::log2(const bigint& input) {
        if (is_negative(input) || input == 0)
            throw std::domain_error("Invalid input for natural log");

        if (input == 1)
            return 0;

        if (input.vec.size() == 1) {
            return std::log2(input.vec.back());
        }

        bigint exponent = 0;
        while (pow(2, exponent) <= input) {
            ++exponent;
        }

        return exponent;
        // TODO: Convert to using division after checking bigO of division vs multiplication
        //    std::string logVal = "-1";
        //    while(s != "0") {
        //        logVal = add(logVal, "1");
        //        s = divide(s, "2");
        //    }
        //    return logVal;
    }

    inline bigint bigint::log10(const bigint& input) {
        if (is_negative(input) || input == 0)
            throw std::domain_error("Invalid input for log base 10");

        if (input == 1)
            return 0;

        return count_digits(input) - 1;
    }

    inline bigint bigint::logwithbase(const bigint& input, const bigint& base) {
        auto top = log2(input);
        auto bottom = log2(base);
        auto answer = divide(top, bottom);
        return answer;
    }

    inline bigint bigint::antilog2(const bigint& input) {
        return pow(2, input);
    }

    inline bigint bigint::antilog10(const bigint& input) {
        return pow(10, input);
    }

    inline void bigint::swap(bigint& lhs, bigint& rhs) {
        const bigint temp = lhs;
        lhs = rhs;
        rhs = temp;
    }

    inline bigint bigint::gcd(const bigint& lhs, const bigint& rhs) {
        bigint temp_l = lhs, temp_r = rhs, remainder;
        if (rhs > lhs)
            swap(temp_l, temp_r);

        while (rhs > 0) {
            remainder = temp_l % temp_r;
            temp_l = temp_r;
            temp_r = remainder;
        }
        return temp_l;
    }

    inline bigint bigint::factorial(const bigint& input) {
        if (is_negative(input)) {
            throw std::runtime_error("Factorial of Negative Integer is not defined.");
        }
        if (input == 0)
            return 1;

        bigint ans = 1;
        bigint temp = input;
        while (temp != 0) {
            ans *= temp;
            temp -= 1;
        }
        return ans;
    }

    /* Simplest form of prime checking, implement your own
     */
    inline bool bigint::is_prime(const bigint& s) {
        if (is_negative(s) || s == 1)
            return false;

        if (s == 2 || s == 3 || s == 5)
            return true;

        if (is_even(s) || s % 5 == 0)
            return false;

        for (bigint i = 3; i * i <= s; i += 2) {
            if ((s % i) == 0) {
                return false;
            }
        }
        return true;
    }

    inline bigint bigint::random(const size_t length) {
        constexpr char charset[] = "0123456789";
        std::default_random_engine rng(std::random_device{}());

        // Distribution for the first digit (1-9)
        std::uniform_int_distribution<> first_dist(1, 9);
        // Distribution for the other digits (0-9)
        std::uniform_int_distribution<> dist(0, 9);

        // Lambda to generate the first character
        auto randchar_first = [charset, &first_dist, &rng]() { return charset[first_dist(rng)]; };
        // Lambda to generate subsequent characters
        auto randchar = [charset, &dist, &rng]() { return charset[dist(rng)]; };

        // Create a string with the specified length
        std::string str(length, 0);

        // Generate the first character separately to ensure it's not '0'
        str[0] = randchar_first();

        // Generate the remaining characters
        std::generate_n(str.begin() + 1, length - 1, randchar);

        return {str};
    }

    inline std::vector<long long> bigint::string_to_vector(std::string input) {
        // Break into chunks of 9 characters
        std::vector<long long> result;
        constexpr int chunk_size = 9;
        const int size = input.size();

        if (size > chunk_size) {
            // Pad the length to get appropriate sized chunks
            if (int mod = size % chunk_size; mod != 0) {
                input.insert(0, chunk_size - mod, '0');
            }
        }
        for (int i = 0; i < input.size(); i += chunk_size) {
            std::string temp_str = input.substr(i, chunk_size);
            result.emplace_back(stoll(temp_str));
        }

        return result;
    }

    inline std::vector<long long> bigint::hex_to_vector(std::string input) {
        // Strip "0x" prefix
        const std::string hex = input.substr(2);

        std::vector<long long> result = {0};

        for (const char c : hex) {
            unsigned long long digit;
            if (c >= '0' && c <= '9')      digit = c - '0';
            else if (c >= 'a' && c <= 'f') digit = c - 'a' + 10;
            else if (c >= 'A' && c <= 'F') digit = c - 'A' + 10;
            else throw std::runtime_error("Invalid hex character.");

            // Multiply current value by 16 and add digit.
            // Max intermediate value: (MAX_SIZE-1)*16+15 = 15,999,999,999
            // which fits in unsigned long long.
            unsigned long long carry = digit;
            for (int i = static_cast<int>(result.size()) - 1; i >= 0; --i) {
                const unsigned long long val = static_cast<unsigned long long>(result[i]) * 16 + carry;
                result[i] = static_cast<long long>(val % static_cast<unsigned long long>(MAX_SIZE));
                carry = val / static_cast<unsigned long long>(MAX_SIZE);
            }
            // carry <= 15 < MAX_SIZE, so this loop runs at most once
            while (carry > 0) {
                result.insert(result.begin(), static_cast<long long>(carry % static_cast<unsigned long long>(MAX_SIZE)));
                carry /= static_cast<unsigned long long>(MAX_SIZE);
            }
        }

        return result;
    }

    inline std::string bigint::vector_to_string(const std::vector<long long>& input) {
        std::stringstream ss;
        bool first = true;
        for (const auto partial : input) {
            if (first) {
                ss << partial; // No padding for the first number
                first = false;
            }
            else {
                ss << std::setw(9) << std::setfill('0') << partial; // Pad to 9 digits
            }
        }
        return ss.str();
    }

    inline int bigint::count_digits(const bigint& input) {
        std::string my_string = vector_to_string(input.vec);
        return static_cast<int>(my_string.length());
    }
} // namespace::BigInt

template<>
struct std::hash<BigInt::bigint>
{
    std::size_t operator()(const BigInt::bigint& input) const noexcept {
        std::size_t seed = input.vec.size();
        for (auto x : input.vec) {
            x = ((x >> 16) ^ x) * 0x45d9f3b;
            x = ((x >> 16) ^ x) * 0x45d9f3b;
            x = (x >> 16) ^ x;
            seed ^= x + 0x9e3779b9 + (seed << 6) + (seed >> 2);
        }
        if (input.is_neg) {
            seed ^= 0x9e3779b9 + (seed << 6) + (seed >> 2);
        }
        return seed;
    }
};

#endif /* BIGINT_H_ */

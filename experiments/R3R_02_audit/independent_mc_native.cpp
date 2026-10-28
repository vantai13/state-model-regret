// Independent L3R.3 physical Monte Carlo; responsible: Doan Van Tai.
// Specification-only implementation. No repository engine headers or libraries.
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <random>

namespace {
using Engine = std::mt19937_64;

// Number of slots using the present mode, including the present slot.
// A geometric run generates the EXACT discrete R2 skeleton, not CTMC jumps.
std::uint64_t run_length(Engine& rng, double keep, std::uint64_t remaining) {
    if (keep >= 1.0) return remaining + 1;
    if (keep <= 0.0) return 1;
    double u = std::generate_canonical<double, 53>(rng);
    if (u == 0.0) u = std::numeric_limits<double>::min();
    const double length = std::floor(std::log(u) / std::log(keep)) + 1.0;
    return length > static_cast<double>(remaining)
        ? remaining + 1 : static_cast<std::uint64_t>(length);
}

// Sum the endpoint occupancies for L equal-increment reflected updates.
double occupancy(double& q, double increment, std::uint64_t length) {
    const double count = static_cast<double>(length);
    double positive_count = count;
    if (increment < 0.0 && q + count * increment <= 0.0) {
        positive_count = std::clamp(std::ceil(q / (-increment)) - 1.0, 0.0, count);
    }
    const double area = positive_count * q
        + increment * positive_count * (positive_count + 1.0) * 0.5;
    q = std::max(0.0, q + count * increment);
    return std::max(0.0, area);
}
}

extern "C" {
int independent_mc_age(std::size_t n, const double* initial_q,
        const std::uint8_t* initial_mode, double lambda, double managed,
        double mu, double dt, double kappa, std::uint64_t slots,
        std::uint64_t seed, double* final_q, std::uint8_t* final_mode) {
    Engine rng(seed);
    const double keep = kappa == 0.0 ? 0.5
        : 0.5 * (1.0 + std::exp(-2.0 * dt / kappa));
    for (std::size_t i = 0; i < n; ++i) {
        double q = initial_q[i];
        std::uint8_t mode = initial_mode[i];
        std::uint64_t remaining = slots;
        while (remaining) {
            const auto run = run_length(rng, keep, remaining);
            const auto used = std::min(run, remaining);
            const double step = (lambda + (mode ? 6.0 : -6.0) + managed - mu) * dt;
            occupancy(q, step, used);
            remaining -= used;
            // Transition AFTER the last occupied slot, including the age endpoint.
            if (run == used) mode ^= 1;
        }
        final_q[i] = q;
        final_mode[i] = mode;
    }
    return 0;
}

int independent_mc_future(std::size_t n, const double* initial_q,
        const std::uint8_t* initial_mode, double lambda, double managed_stay,
        double managed_switch, double mu, double dt, double kappa,
        std::uint64_t slots, std::uint64_t seed, double* cost_stay,
        double* cost_switch) {
    Engine rng(seed);
    const double keep = kappa == 0.0 ? 0.5
        : 0.5 * (1.0 + std::exp(-2.0 * dt / kappa));
    for (std::size_t i = 0; i < n; ++i) {
        double q0 = initial_q[i], q1 = initial_q[i], c0 = 0.0, c1 = 0.0;
        std::uint8_t mode = initial_mode[i];
        std::uint64_t remaining = slots;
        while (remaining) {
            const auto run = run_length(rng, keep, remaining);
            const auto used = std::min(run, remaining);
            const double background_net = lambda + (mode ? 6.0 : -6.0) - mu;
            c0 += occupancy(q0, (background_net + managed_stay) * dt, used);
            c1 += occupancy(q1, (background_net + managed_switch) * dt, used);
            remaining -= used;
            if (run == used) mode ^= 1;
        }
        cost_stay[i] = dt * c0;
        cost_switch[i] = dt * c1;
    }
    return 0;
}
}

#include <optional>
#include <coroutine>

template<movable T>
class generator
{
public:
    struct promise_type
    {
        generator<T> get_return_object()
        {
            return generator{Handle::from_promise(*this)};
        }
        static suspend_always initial_suspend() noexcept
        {
            return {};
        }
        static suspend_always final_suspend() noexcept
        {
            return {};
        }
        suspend_always yield_value(T value) noexcept
        {
            current_value = move(value);
            return {};
        }
        // Disallow co_await in generator coroutines.
        void await_transform() = delete;
        [[noreturn]]
        static void unhandled_exception() { throw; }

        optional<T> current_value;
    };

    using Handle = coroutine_handle<promise_type>;

    explicit generator(const Handle coroutine) :
        m_coroutine{coroutine}
    {}

    generator() = default;
    ~generator()
    {
        if (m_coroutine)
            m_coroutine.destroy();
    }

    generator(const generator&) = delete;
    generator& operator=(const generator&) = delete;

    generator(generator&& other) noexcept :
        m_coroutine{other.m_coroutine}
    {
        other.m_coroutine = {};
    }
    generator& operator=(generator&& other) noexcept
    {
        if (this != &other)
        {
            if (m_coroutine)
                m_coroutine.destroy();
            m_coroutine = other.m_coroutine;
            other.m_coroutine = {};
        }
        return *this;
    }

    // Range-based for loop support.
    class Iter
    {
    public:
        void operator++()
        {
            m_coroutine.resume();
        }
        const T& operator*() const
        {
            return *m_coroutine.promise().current_value;
        }
        bool operator==(default_sentinel_t) const
        {
            return !m_coroutine || m_coroutine.done();
        }

        explicit Iter(const Handle coroutine) :
            m_coroutine{coroutine}
        {}

    private:
        Handle m_coroutine;
    };

    Iter begin()
    {
        if (m_coroutine)
            m_coroutine.resume();
        return Iter{m_coroutine};
    }

    default_sentinel_t end() { return {}; }

private:
    Handle m_coroutine;
};

import { render, screen } from '@testing-library/react'
import { ThemeProvider, useTheme } from '../context/ThemeContext'

describe('ThemeContext', () => {
  it('provides theme context', () => {
    const TestComponent = () => {
      const { theme } = useTheme()
      return <div data-testid="theme">{theme}</div>
    }

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    )

    expect(screen.getByTestId('theme')).toHaveTextContent('dark')
  })

  it('toggles theme', () => {
    const TestComponent = () => {
      const { theme, toggleTheme } = useTheme()
      return (
        <div>
          <div data-testid="theme">{theme}</div>
          <button onClick={toggleTheme}>Toggle</button>
        </div>
      )
    }

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    )

    const toggleButton = screen.getByText('Toggle')
    toggleButton.click()

    expect(screen.getByTestId('theme')).toHaveTextContent('light')
  })
})

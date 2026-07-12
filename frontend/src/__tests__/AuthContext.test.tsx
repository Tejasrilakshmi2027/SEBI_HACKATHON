import { render, screen, waitFor } from '@testing-library/react'
import { AuthProvider, useAuth } from '../context/AuthContext'

describe('AuthContext', () => {
  it('provides auth context', () => {
    const TestComponent = () => {
      const { user, isAuthenticated } = useAuth()
      return (
        <div>
          <div data-testid="authenticated">{isAuthenticated ? 'true' : 'false'}</div>
          <div data-testid="user">{user ? user.email : 'null'}</div>
        </div>
      )
    }

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    expect(screen.getByTestId('authenticated')).toHaveTextContent('false')
    expect(screen.getByTestId('user')).toHaveTextContent('null')
  })

  it('handles login', async () => {
    const TestComponent = () => {
      const { login, isAuthenticated } = useAuth()
      return (
        <div>
          <div data-testid="authenticated">{isAuthenticated ? 'true' : 'false'}</div>
          <button onClick={() => login('test@example.com', 'password')}>
            Login
          </button>
        </div>
      )
    }

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    const loginButton = screen.getByText('Login')
    loginButton.click()

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true')
    })
  })
})

import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import App from '../App'

describe('App', () => {
  it('renders without crashing', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )
  })

  it('renders the landing page by default', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )
    // Check for landing page elements
    expect(screen.getByText(/SEBI Sentinel AI/i)).toBeInTheDocument()
  })
})

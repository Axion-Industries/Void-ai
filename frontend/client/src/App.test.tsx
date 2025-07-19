import { render, screen } from '@testing-library/react';
import App from './App';

describe('App', () => {
  it('renders sign in form when not authenticated', () => {
    render(<App />);
    expect(screen.getByText(/sign in/i)).toBeInTheDocument();
  });
});

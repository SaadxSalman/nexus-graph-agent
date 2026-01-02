// client/__tests__/login.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import LoginPage from '@/app/auth/login/page';

test('shows error message on failed login', async () => {
  server.use(rest.post('/api/auth', (req, res, ctx) => res(ctx.status(401))));
  render(<LoginPage />);
  
  fireEvent.click(screen.getByText(/sign in/i));
  expect(await screen.findByText(/invalid credentials/i)).toBeInTheDocument();
});
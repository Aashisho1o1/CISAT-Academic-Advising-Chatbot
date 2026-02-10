import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import App from './App';
import * as api from './api';

jest.mock('./api', () => {
  const actual = jest.requireActual('./api');
  return {
    ...actual,
    getCurrentUser: jest.fn(),
    logout: jest.fn(),
    login: jest.fn(),
  };
});

const mockedGetCurrentUser = api.getCurrentUser as jest.MockedFunction<typeof api.getCurrentUser>;
const mockedLogout = api.logout as jest.MockedFunction<typeof api.logout>;

describe('App auth routing', () => {
  const mockConfig = { headers: {} } as InternalAxiosRequestConfig;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('shows login screen when user is not authenticated', async () => {
    mockedGetCurrentUser.mockRejectedValue(new Error('Unauthorized'));

    render(<App />);

    expect(await screen.findByText('Login to Academic Advising System')).toBeInTheDocument();
  });

  it('loads session user and logs out successfully', async () => {
    const currentUserResponse: AxiosResponse<{ user: api.User }> = {
      data: { user: { id: 1, username: 'test-user', role: 'user' } },
      status: 200,
      statusText: 'OK',
      headers: {},
      config: mockConfig,
    };
    const logoutResponse: AxiosResponse<{ message: string }> = {
      data: { message: 'Logged out' },
      status: 200,
      statusText: 'OK',
      headers: {},
      config: mockConfig,
    };

    mockedGetCurrentUser.mockResolvedValue(currentUserResponse);
    mockedLogout.mockResolvedValue(logoutResponse);

    render(<App />);

    expect(await screen.findByText(/Welcome, test-user!/i)).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: /logout/i }));

    await waitFor(() => {
      expect(screen.getByRole('link', { name: /login/i })).toBeInTheDocument();
    });

    expect(mockedLogout).toHaveBeenCalledTimes(1);
  });
});

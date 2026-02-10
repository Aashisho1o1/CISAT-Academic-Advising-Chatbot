describe('API base URL resolution', () => {
  const originalApiBase = process.env.REACT_APP_API_BASE_URL;

  afterEach(() => {
    jest.resetModules();
    if (typeof originalApiBase === 'undefined') {
      delete process.env.REACT_APP_API_BASE_URL;
    } else {
      process.env.REACT_APP_API_BASE_URL = originalApiBase;
    }
  });

  it('uses REACT_APP_API_BASE_URL when provided', () => {
    process.env.REACT_APP_API_BASE_URL = 'https://example.com/api';

    const apiModule = require('./api') as typeof import('./api');

    expect(apiModule.resolveApiBaseUrl()).toBe('https://example.com/api');
    expect(apiModule.API_BASE_URL).toBe('https://example.com/api');
  });

  it('falls back to localhost default when env var is missing', () => {
    delete process.env.REACT_APP_API_BASE_URL;

    const apiModule = require('./api') as typeof import('./api');

    expect(apiModule.resolveApiBaseUrl()).toBe('http://localhost:8000/api');
    expect(apiModule.API_BASE_URL).toBe('http://localhost:8000/api');
  });
});

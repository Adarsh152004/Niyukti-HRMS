/**
 * DataProvider — isolates demo mode from production.
 *
 * NEVER use demo fixtures when VITE_APP_MODE=production.
 * NEVER silently fall back to fixtures on API failure.
 */

const APP_MODE = import.meta.env.VITE_APP_MODE ?? 'production';

export const IS_DEMO_MODE = APP_MODE === 'demo';

/**
 * Wraps a production API call with demo-mode isolation.
 * In demo mode, returns the fixture immediately.
 * In production mode, always calls the real API.
 */
export async function withDataProvider<T>(
  productionFetch: () => Promise<T>,
  demoFixture: T
): Promise<T> {
  if (IS_DEMO_MODE) {
    // Simulate realistic async latency
    await new Promise((r) => setTimeout(r, 120));
    return demoFixture;
  }
  return productionFetch();
}

/** Executes a mutation — no-ops in demo mode with a clear message. */
export async function withDemoAwareMutation<T>(
  productionAction: () => Promise<T>,
  demoResult: T
): Promise<{ result: T; wasDemo: boolean }> {
  if (IS_DEMO_MODE) {
    await new Promise((r) => setTimeout(r, 200));
    return { result: demoResult, wasDemo: true };
  }
  const result = await productionAction();
  return { result, wasDemo: false };
}

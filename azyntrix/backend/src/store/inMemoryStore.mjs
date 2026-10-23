import { initialJobs } from '../seed/seedData.mjs';

/**
 * Shared In-Memory Data Store for Azyntrix Backend
 * Ensures that AI Agent postings (agentController) and Public Website queries (jobController)
 * share the exact same synchronized in-memory state when running in resilient local dev mode.
 */

export const inMemoryJobs = initialJobs.map(j => ({ ...j }));
export const inMemoryApplications = [];
export const inMemoryInquiries = [];

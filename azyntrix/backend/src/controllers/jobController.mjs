import { JobModel } from '../models/Job.mjs';
import { initialJobs } from '../seed/seedData.mjs';
import { getDBStatus } from '../config/db.mjs';

// In-memory fallback repository
let inMemoryJobs = [...initialJobs];

export async function getJobs(req, res) {
  try {
    const { department, search } = req.query;
    const dbStatus = getDBStatus();

    let jobs;
    if (dbStatus.connected) {
      const query = { isActive: true };
      if (department && department !== 'all') {
        query.department = department;
      }
      if (search) {
        query.$or = [
          { title: { $regex: search, $options: 'i' } },
          { techStack: { $regex: search, $options: 'i' } },
        ];
      }
      jobs = await JobModel.find(query).sort({ createdAt: -1 });
    } else {
      // Use in-memory fallback
      jobs = inMemoryJobs.filter(job => {
        const matchesDept = !department || department === 'all' || job.department === department;
        const matchesSearch = !search || 
          job.title.toLowerCase().includes(search.toLowerCase()) ||
          job.techStack.some(t => t.toLowerCase().includes(search.toLowerCase()));
        return matchesDept && matchesSearch && job.isActive;
      });
    }

    return res.status(200).json({
      success: true,
      count: jobs.length,
      data: jobs,
      meta: {
        source: dbStatus.connected ? 'mongodb_atlas' : 'resilient_cache',
      }
    });
  } catch (error) {
    console.error('[JobController] Error fetching jobs:', error);
    return res.status(500).json({
      success: false,
      error: 'Failed to retrieve guild job positions',
      message: error.message,
    });
  }
}

export async function getJobById(req, res) {
  try {
    const { jobId } = req.params;
    const dbStatus = getDBStatus();

    let job;
    if (dbStatus.connected) {
      job = await JobModel.findOne({ id: jobId, isActive: true });
    } else {
      job = inMemoryJobs.find(j => j.id === jobId && j.isActive);
    }

    if (!job) {
      return res.status(404).json({
        success: false,
        error: `Job position with ID "${jobId}" was not found or is no longer active.`,
      });
    }

    return res.status(200).json({
      success: true,
      data: job,
    });
  } catch (error) {
    console.error('[JobController] Error fetching job by ID:', error);
    return res.status(500).json({
      success: false,
      error: 'Failed to retrieve job specification',
      message: error.message,
    });
  }
}

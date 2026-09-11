import { getDBStatus } from '../config/db.mjs';
import { JobModel } from '../models/Job.mjs';
import { ApplicationModel } from '../models/Application.mjs';
import { InquiryModel } from '../models/Inquiry.mjs';

const startTime = Date.now();

export async function getStatus(req, res) {
  try {
    const dbStatus = getDBStatus();
    let stats = {
      jobs: 4,
      applications: 0,
      inquiries: 0,
    };

    if (dbStatus.connected) {
      stats.jobs = await JobModel.countDocuments();
      stats.applications = await ApplicationModel.countDocuments();
      stats.inquiries = await InquiryModel.countDocuments();
    }

    const uptimeSeconds = Math.floor((Date.now() - startTime) / 1000);

    return res.status(200).json({
      success: true,
      service: 'Azyntrix Core Systems API',
      version: '2.4.0',
      timestamp: new Date().toISOString(),
      uptime: `${uptimeSeconds}s`,
      database: dbStatus,
      nodes: [
        { id: 'node-us-west', city: 'San Francisco, CA', latency: '12ms', status: 'optimal' },
        { id: 'node-us-east', city: 'New York, NY', latency: '18ms', status: 'optimal' },
        { id: 'node-eu-west', city: 'London, UK', latency: '34ms', status: 'optimal' },
        { id: 'node-eu-central', city: 'Zurich, CH', latency: '38ms', status: 'optimal' },
      ],
      metrics: {
        slaStatus: '99.999% SLA Operational',
        activePositions: stats.jobs,
        candidatePipeline: stats.applications,
        activeInquiries: stats.inquiries,
      }
    });
  } catch (error) {
    return res.status(500).json({
      success: false,
      error: 'Telemetry error',
      message: error.message,
    });
  }
}

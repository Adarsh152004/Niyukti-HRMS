import mongoose from 'mongoose';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load root .env from HRMS root
dotenv.config({ path: path.resolve(__dirname, '../../../.env') });

const MONGO_URI = process.env.MONGO_CONNECTION_STRING || 'mongodb://localhost:27017/azyntrix';
const DB_NAME = 'azyntrix';

let isConnected = false;
let isInMemoryFallback = false;

export async function connectDB() {
  if (isConnected) return;

  try {
    console.log(`[Azyntrix Backend] Connecting to MongoDB Atlas cluster...`);
    
    // Connect with Mongoose
    await mongoose.connect(MONGO_URI, {
      dbName: DB_NAME,
      serverSelectionTimeoutMS: 5000,
      connectTimeoutMS: 10000,
    });

    isConnected = true;
    isInMemoryFallback = false;
    console.log(`[Azyntrix Backend] ✅ Successfully connected to MongoDB Database: "${DB_NAME}"`);
  } catch (error) {
    console.warn(`[Azyntrix Backend] ⚠️ MongoDB Atlas direct connection warning: ${error.message}`);
    console.log(`[Azyntrix Backend] Enabling resilient in-memory storage fallback mode for seamless local operation.`);
    isConnected = false;
    isInMemoryFallback = true;
  }
}

export function getDBStatus() {
  return {
    connected: isConnected,
    mode: isInMemoryFallback ? 'resilient_in_memory' : 'mongodb_atlas',
    database: DB_NAME,
    state: mongoose.connection.readyState,
  };
}

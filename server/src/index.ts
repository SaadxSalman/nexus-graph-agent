import express from 'express';
import mongoose from 'mongoose';
import dotenv from 'dotenv';
import cors from 'cors';

// 1. Load environment variables immediately
dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// 2. Configure CORS (Middleware)
app.use(cors({
  origin: process.env.CLIENT_URL,
  methods: ["GET", "POST", "PUT", "DELETE"],
  credentials: true
}));

// 3. Built-in middleware to parse JSON
app.use(express.json());

// 4. Initialize MongoDB Connection
mongoose.connect(process.env.MONGODB_URI!)
  .then(() => {
    console.log("✅ MongoDB Connected");
    // Start server only after DB connection is successful
    app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));
  })
  .catch(err => console.error("❌ MongoDB connection error:", err));
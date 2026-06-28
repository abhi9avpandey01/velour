import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  /* Enable standalone output for Docker deployments */
  output: 'standalone',

  /* Disable telemetry */
  telemetry: false,
};

export default nextConfig;

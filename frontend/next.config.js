/** @type {import('next').NextConfig} */
const API = process.env.FASTAPI_URL || "http://127.0.0.1:8070";

const nextConfig = {
  async rewrites() {
    return [
      { source: "/v1/:path*", destination: `${API}/v1/:path*` },
      { source: "/healthz", destination: `${API}/healthz` },
    ];
  },
};

module.exports = nextConfig;

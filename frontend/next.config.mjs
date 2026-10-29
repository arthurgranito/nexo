const apiProxyTarget = process.env.API_PROXY_TARGET || "http://127.0.0.1:8000";

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  async rewrites() {
    return [
      { source: "/v1/:path*", destination: `${apiProxyTarget}/v1/:path*` },
      { source: "/health", destination: `${apiProxyTarget}/health` },
      { source: "/ready", destination: `${apiProxyTarget}/ready` },
    ];
  },
};

export default nextConfig;

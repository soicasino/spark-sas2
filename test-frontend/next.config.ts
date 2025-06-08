import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* Raspberry Pi 4 optimizations */

  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  },

  // API proxy for CORS and network issues
  async rewrites() {
    return [
      {
        source: "/api/proxy/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/:path*`,
      },
    ];
  },

  // Performance optimizations for Raspberry Pi
  experimental: {
    optimizeCss: true,
  },

  // Compress responses
  compress: true,

  // Optimize images for Pi's limited resources
  images: {
    formats: ["image/webp"],
    minimumCacheTTL: 60,
    dangerouslyAllowSVG: true,
  },

  // Output configuration for better Pi performance
  output: "standalone",

  // Reduce bundle size
  webpack: (config, { dev, isServer }) => {
    // Optimize for production on Pi
    if (!dev && !isServer) {
      config.optimization.splitChunks.cacheGroups = {
        default: false,
        vendors: false,
        vendor: {
          name: "vendor",
          chunks: "all",
          test: /node_modules/,
        },
      };
    }
    return config;
  },

  // Network timeouts for Pi network conditions
  async headers() {
    return [
      {
        source: "/api/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=60, stale-while-revalidate=300",
          },
        ],
      },
    ];
  },
};

export default nextConfig;

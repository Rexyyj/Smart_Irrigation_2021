const webpack = require("webpack");

module.exports = {
  resolve: {
    fallback: {
      url: require.resolve("url/"),
      buffer: require.resolve("buffer/"),
      process: require.resolve('process/'),
    },
  },
  plugins: [
    new webpack.ProvidePlugin({
      Buffer: ["buffer", "Buffer"],
    }),
    new webpack.ProvidePlugin({
      process: ['process'],
    }),
  ],
};

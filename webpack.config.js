const path = require("path");
const BundleTracker = require("webpack-bundle-tracker");
const CopyPlugin = require("copy-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const webpack = require("webpack");

module.exports = {
  entry: {
    sentry: "./assets/javascript/sentry.js",
    global: ["./assets/javascript/global.js", "./assets/scss/global.scss"],
    "cookie-policy-form": "./assets/javascript/cookie-policy-form.js",
    "business-details": "./assets/javascript/business-details.js",
  },

  output: {
    path: path.resolve("./build/assets/"),
    publicPath: "/static/",
    filename: "[name]-[fullhash].js",
  },

  plugins: [
    new BundleTracker({ filename: "./webpack-stats.json" }),
    new MiniCssExtractPlugin({
      filename: "[name]-[fullhash].css",
      chunkFilename: "[id]-[fullhash].css",
    }),
    new CopyPlugin({
      patterns: [{ from: "./assets/images/", to: "images" }],
    }),
    new webpack.DefinePlugin({
      SENTRY_DSN: JSON.stringify(process.env.SENTRY_DSN),
      SENTRY_ENVIRONMENT: JSON.stringify(process.env.SENTRY_ENVIRONMENT),
    }),
  ],

  module: {
    rules: [
      {
        test: /\.m?js$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
          options: {
            presets: ['@babel/preset-env']
          }
        }
      },

      // Use file-loader to handle image assets
      {
        test: /\.(png|jpe?g|gif|woff2?|svg|ico|eot)$/i,
        use: [
          {
            loader: "file-loader",
            options: {
              // Note: `django-webpack-loader`'s `webpack_static` tag does
              //       not yet pick up versioned assets, so we need to
              //       generate image assets without a hash in the
              //       filename.
              // c.f.: https://github.com/owais/django-webpack-loader/issues/138
              name: "[name].[ext]",
            },
          },
        ],
      },

      // Extract compiled SCSS separately from JS
      {
        test: /\.s[ac]ss$/i,
        use: [
          {
            loader: MiniCssExtractPlugin.loader,
          },
          "css-loader",
          "sass-loader",
        ],
      },
    ],
  },

  resolve: {
    modules: ["node_modules"],
    extensions: [".js", ".scss"],
  },
};

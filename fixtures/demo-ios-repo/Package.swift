// swift-tools-version: 5.9

import PackageDescription

let package = Package(
    name: "DemoCodexMaintainerApp",
    platforms: [.iOS(.v17)],
    products: [
        .library(name: "DemoCodexMaintainerApp", targets: ["DemoCodexMaintainerApp"])
    ],
    targets: [
        .target(name: "DemoCodexMaintainerApp"),
        .testTarget(name: "DemoCodexMaintainerAppTests", dependencies: ["DemoCodexMaintainerApp"])
    ]
)

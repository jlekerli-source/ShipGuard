// swift-tools-version: 5.9

import PackageDescription

let package = Package(
    name: "DemoShipGuardApp",
    platforms: [.iOS(.v17)],
    products: [
        .library(name: "DemoShipGuardApp", targets: ["DemoShipGuardApp"])
    ],
    targets: [
        .target(name: "DemoShipGuardApp"),
        .testTarget(name: "DemoShipGuardAppTests", dependencies: ["DemoShipGuardApp"])
    ]
)

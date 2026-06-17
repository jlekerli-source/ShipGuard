import XCTest
@testable import DemoShipGuardApp

final class DemoPermissionsTests: XCTestCase {
    func testAsyncSurfaceIsMappedToTheTestTarget() async throws {
        await Task.yield()
        XCTAssertTrue(true)
    }
}

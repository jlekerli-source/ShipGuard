import ActivityKit
import AlarmKit
import AppIntents
import CoreLocation
import StoreKit
import SwiftUI
import UserNotifications
import WidgetKit

struct DemoAlarmIntent: AppIntent {
    static var title: LocalizedStringResource = "Start demo alarm"

    func perform() async throws -> some IntentResult {
        _ = CLLocationManager()
        _ = UNUserNotificationCenter.current()
        _ = Product.self
        return .result()
    }
}

struct DemoWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "demo", provider: DemoProvider()) { _ in
            Text("Demo")
        }
    }
}

struct DemoProvider: TimelineProvider {
    func placeholder(in context: Context) -> DemoEntry {
        DemoEntry()
    }

    func getSnapshot(in context: Context, completion: @escaping (DemoEntry) -> Void) {
        completion(DemoEntry())
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<DemoEntry>) -> Void) {
        completion(Timeline(entries: [DemoEntry()], policy: .never))
    }
}

struct DemoEntry: TimelineEntry {
    let date = Date()
}

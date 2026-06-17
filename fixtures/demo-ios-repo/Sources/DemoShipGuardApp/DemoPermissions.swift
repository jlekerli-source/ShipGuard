import ActivityKit
import AlarmKit
import AppIntents
import CoreLocation
import Foundation
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

@MainActor
struct DemoPerformanceHotspots: View {
    var body: some View {
        TimelineView(.periodic(from: .now, by: 1.0 / 30.0)) { timeline in
            let formatter = DateFormatter()
            Text(formatter.string(from: timeline.date))
                .blur(radius: 30)
                .shadow(color: .black.opacity(0.2), radius: 8)
                .shadow(color: .blue.opacity(0.2), radius: 12)
                .shadow(color: .purple.opacity(0.2), radius: 16)
                .onAppear {
                    withAnimation(.easeInOut(duration: 2).repeatForever()) {}
                    UNUserNotificationCenter.current().removePendingNotificationRequests(withIdentifiers: ["demo"])
                }
        }
    }
}

import 'package:drift/drift.dart';

// Tables definition for local storage
class LocalAppEvents extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get eventUuid => text()();
  TextColumn get packageName => text()();
  DateTimeColumn get startTime => dateTime()();
  DateTimeColumn get endTime => dateTime()();
  IntColumn get durationSeconds => integer()();
  BoolColumn get synced => boolean().withDefault(const Constant(false))();
}

class LocalScreenEvents extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get eventUuid => text()();
  TextColumn get eventType => text()(); // 'SCREEN_ON', 'SCREEN_OFF', 'USER_UNLOCKED'
  DateTimeColumn get timestamp => dateTime()();
  BoolColumn get synced => boolean().withDefault(const Constant(false))();
}

class LocalNetworkEvents extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get eventUuid => text()();
  TextColumn get packageName => text()();
  IntColumn get wifiBytesRx => integer().withDefault(const Constant(0))();
  IntColumn get wifiBytesTx => integer().withDefault(const Constant(0))();
  IntColumn get mobileBytesRx => integer().withDefault(const Constant(0))();
  IntColumn get mobileBytesTx => integer().withDefault(const Constant(0))();
  TextColumn get calendarDate => text()();
  BoolColumn get synced => boolean().withDefault(const Constant(false))();
}

class SyncQueue extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get batchId => text()();
  TextColumn get payloadJson => text()();
  TextColumn get status => text().withDefault(const Constant('PENDING'))(); // PENDING, IN_FLIGHT, COMPLETED, FAILED
  IntColumn get attemptCount => integer().withDefault(const Constant(0))();
  DateTimeColumn get createdAt => dateTime()();
}

@DriftDatabase(tables: [LocalAppEvents, LocalScreenEvents, LocalNetworkEvents, SyncQueue])
class AppDatabase {
  final QueryExecutor executor;
  AppDatabase(this.executor);

  int get schemaVersion => 1;
}

// Create a text parameter DataFolder containing the absolute generated data path.
// Create a blank query named LoadCsv and paste this function in Advanced Editor.
(FileName as text, Types as list) as table =>
let
    Source = Csv.Document(File.Contents(DataFolder & "/" & FileName),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, Types, "en-US")
in
    Typed

// Separate query named Orders (paste the expression below in its own query):
// LoadCsv("orders.csv", {{"order_id", Int64.Type}, {"session_id", Int64.Type},
// {"user_id", Int64.Type}, {"order_date", type date}, {"status", type text},
// {"delivery_fee", Currency.Type}, {"discount", Currency.Type},
// {"delivery_time_min", type number}, {"gross_revenue", Currency.Type},
// {"net_revenue", Currency.Type}})

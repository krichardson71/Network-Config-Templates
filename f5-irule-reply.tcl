when HTTP_REQUEST {
# High speed logging
    set hslpool pool-high-speed-logging-splunk
    set hsl [HSL::open -proto UDP -pool $hslpool]

	if { [active_members [LB::server pool]] == 0 } {
      HTTP::respond 577 content "AQG Bypass Enabled - Primary Nodes Down"

      HSL::send $hslpool "AQG Bypass Enabled - Primary Nodes Down"
  }
    elseif { [HTTP::uri] contains "/"} {
      HTTP::respond 577 content "AQG Bypass Enabled - Primary Nodes Up"
      
      HSL::send $hslpool "AQG Bypass Enabled - Primary Nodes Up"
  }
}

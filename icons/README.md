# Icons

Use any of these as `icon:<name>` in a node. Every icon is under an open licence; sources and changes are in
[`NOTICE.md`](NOTICE.md). List them any time with `python3 build.py --list-icons`.

| Preview | Name | Typical use | Licence |
| :---: | --- | --- | --- |
| <img src="router.svg" width="56" alt="router"> | `router` | ISP, WAN and edge routers | Apache-2.0 |
| <img src="switch.svg" width="56" alt="switch"> | `switch` | core, access and L3 switches | Apache-2.0 |
| <img src="firewall.svg" width="56" alt="firewall"> | `firewall` | firewalls, NGFW, IPS | Apache-2.0 |
| <img src="server.svg" width="84" alt="server"> | `server` | a single server | Apache-2.0 |
| <img src="rack.svg" width="56" alt="rack"> | `rack` | server racks and farms | Apache-2.0 |
| <img src="cloud.svg" width="72" alt="cloud"> | `cloud` | Internet, WAN, cloud services | MIT |
| <img src="database.svg" width="44" alt="database"> | `database` | databases, storage | MIT |
| <img src="pc.svg" width="56" alt="pc"> | `pc` | workstations | MIT |
| <img src="ap.svg" width="56" alt="ap"> | `ap` | wireless access points | MIT |
| <img src="laptop.svg" width="56" alt="laptop"> | `laptop` | laptops, remote workers | MIT (Tabler) |
| <img src="phone.svg" width="56" alt="phone"> | `phone` | phones, VoIP, mobile | MIT (Tabler) |
| <img src="printer.svg" width="56" alt="printer"> | `printer` | printers, MFPs | MIT (Tabler) |
| <img src="lock.svg" width="56" alt="lock"> | `lock` | VPN gateways, secure zones | MIT (Tabler) |
| <img src="building.svg" width="56" alt="building"> | `building` | sites, offices, data centres | MIT (Tabler) |
| <img src="users.svg" width="56" alt="users"> | `users` | user groups, departments | MIT (Tabler) |

## Adding an icon

1. Save a flat SVG as `icons/<name>.svg`. It needs a `viewBox`; names may contain letters, digits, `_` and `-`.
2. Use `#049FD9` as the main colour to match the set. Put fills and strokes directly on the shapes or on a
   wrapping `<g>`. Don't rely on attributes of the root `<svg>` element: `build.py` only copies its contents.
3. Add it to the table above and record its origin and licence in `NOTICE.md` and `REUSE.toml`.
   Good sources of permissively licensed icons are [Tabler Icons](https://tabler.io/icons) (MIT) and
   [Lucide](https://lucide.dev/) (ISC).

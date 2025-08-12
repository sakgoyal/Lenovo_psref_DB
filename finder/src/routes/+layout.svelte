<script lang="ts">
	import { ModeWatcher } from "mode-watcher";
	let { children } = $props();
</script>

<ModeWatcher themeColors={{ dark: "dark", light: "white" }} />
{@render children()}

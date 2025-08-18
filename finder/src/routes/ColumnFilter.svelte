<script lang="ts">
	import Svelecte from "svelecte";
	let value = $state<string[]>([]);

	type Options = string[];

	type Props = {
		filterName: string;
		options: Options;
	};

	let { filterName, options = ["Column Filter 1", "Filter 2"] }: Props = $props();

	import { MultiSelect } from "flowbite-svelte";

	let multiSelected = $state<string[]>([]);
	let countries = [
		{ value: "us", name: "United States" },
		{ value: "ca", name: "Canada" },
		{ value: "fr", name: "France" },
		{ value: "jp", name: "Japan" },
		{ value: "en", name: "England" },
	];
</script>

<div class="dark">
	<h3>{filterName}</h3>
	<Svelecte bind:value {options} multiple clearable keepSelectionInList={true} />
  <!-- <MultiSelect items={countries} bind:value={multiSelected} /> -->
</div>

<style>
	.dark {
		--sv-min-height: 40px;
		--sv-bg: #32363f;
		--sv-disabled-bg: #eee;
		--sv-border: 1px solid #626262;
		--sv-border-radius: 4px;
		--sv-general-padding: 4px;
		--sv-control-bg: var(--sv-bg);
		--sv-item-wrap-padding: 3px 3px 3px 6px;
		--sv-selection-wrap-padding: 3px 3px 3px 4px;
		--sv-selection-multi-wrap-padding: 3px 3px 3px 6px;
		--sv-item-selected-bg: #626262;
		--sv-item-btn-color: #ccc;
		--sv-item-btn-color-hover: #ccc;
		--sv-item-btn-bg: #626262;
		--sv-item-btn-bg-hover: #bc6063;
		--sv-icon-color: #bbb;
		--sv-icon-color-hover: #ccc;
		--sv-icon-bg: transparent;
		--sv-icon-size: 20px;
		--sv-separator-bg: #626262;
		--sv-btn-border: 0;
		--sv-placeholder-color: #ccccd6;
		--sv-dropdown-bg: var(--sv-bg);
		--sv-dropdown-border: var(--sv-border);
		--sv-dropdown-offset: 1px;
		--sv-dropdown-width: auto;
		--sv-dropdown-shadow: 0 1px 3px #555;
		--sv-dropdown-height: 320px;
		--sv-dropdown-active-bg: #553d3d;
		--sv-dropdown-selected-bg: #754545;
		--sv-create-kbd-border: 1px solid #626262;
		--sv-create-kbd-bg: #626262;
		--sv-create-disabled-bg: #fcbaba;
		--sv-loader-border: 2px solid #626262;
	}
</style>

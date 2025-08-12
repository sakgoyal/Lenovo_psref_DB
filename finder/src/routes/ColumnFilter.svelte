<script lang="ts">
	import Svelecte from "svelecte";
	let value = $state<string[]>([]);

	let {filterName = "Column Filter", options = [{ id: "columnFilter", text: "Column Filter" }] } = $props();


</script>


<div>
	<h3>{filterName}</h3>
	<Svelecte bind:value {options} multiple clearable keepSelectionInList={true} />
</div>

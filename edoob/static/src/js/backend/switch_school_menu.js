/** @odoo-module alias=edoob.SwitchSchoolMenu */

import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

const {Component, QWeb} = owl;
const {useRef} = owl.hooks;


export class SwitchSchoolTree extends Component {
    static template = 'edoob.SwitchSchoolTree'

    jsTreeDivRef = useRef('jsTreeDiv');

    get $jsTreeDiv() {
        return $(this.jsTreeDivRef.el);
    }

    setup() {
        this.schoolService = useService("school");
    }

    getJSTreeJSON() {
        const {availableSchoolDistricts} = this.schoolService;
        const JSONData = [];

        for (const district of availableSchoolDistricts) {
            const districtValues = this.getJSTreeJSONDistrictValues(district);
            JSONData.push(districtValues);
        }

        return JSONData;

    }

    getJSTreeJSONDistrictValues(district) {
        const { availableSchools } = this.schoolService;
        const districtSchools = availableSchools.filter(school => school.district_id === district.id);
        return {
            text: district.name,
            children: districtSchools.map(school => this.getJSTreeJSONSchoolValues(school)),
        }
    }

    getJSTreeJSONSchoolValues(school) {
        const {availableSchoolPrograms} = this.schoolService;
        const schoolPrograms = availableSchoolPrograms.filter(program => program.school_id === school.id && !program.parent_id);
        return {
            text: school.name,
            children: schoolPrograms.map(program => this.getJSTreeJSONProgramValues(program)),
        }
    }

    getJSTreeJSONProgramValues(program) {
        const {availableSchoolPrograms} = this.schoolService;
        const programValues = {
            text: program.name,
            state: {
                checked: this.schoolService.allowedProgramIds.includes(program.id),
                selected: this.schoolService.currentSchoolProgram.id === program.id,
            },
            data : {
                schoolProgramId: program.id
            }
        }
        const children = availableSchoolPrograms.filter(auxProgram => program.child_ids.includes(auxProgram.id) && auxProgram.parent_id === program.id)
        if (children.length) {
            programValues.children = children.map(program => this.getJSTreeJSONProgramValues(program));
        }
        return programValues
    }

    mounted() {
        const res = super.mounted(...arguments)
        const $jsTree = this.$jsTreeDiv.jstree({
            plugins: ['themes', 'html_data', 'checkbox', 'ui', 'changed'],
            core: {
                themes: {
                    icons: false
                },
                check_callback: false,
                data: this.getJSTreeJSON(),
            },
            checkbox: {
                tie_selection: false // for checking without selecting and selecting without checking
            },

        })

        function isSchoolProgramNode(node) {
            return node.data && node.data.schoolProgramId
        }

        function getCheckedProgramNodes() {
            const selectedNodes = $jsTree.jstree().get_checked(true);
            const programNodes = []
            for (let selectedNode of selectedNodes) {
                if (isSchoolProgramNode(selectedNode)) {
                    programNodes.push(selectedNode)
                }
            }
            return programNodes;
        }

        function getSelectedProgramNode(node) {
            let currentNode = node;
            while (true) {
                if (currentNode.children && currentNode.children.length) {
                    const nextNodeId = currentNode.children[0];
                    currentNode = $jsTree.jstree(true).get_node(nextNodeId);
                } else {
                    break;
                }
            }
            return currentNode;
        }

        $jsTree.on('check_node.jstree uncheck_node.jstree', (e, data) => {
            const programNodes = getCheckedProgramNodes();
            let programIds = []
            for (let programNode of programNodes) {
                programIds.push(parseInt(programNode.data.schoolProgramId));
            }
            if (!data.event.target.classList.contains('jstree-checkbox')) {
                const programNode = getSelectedProgramNode(data.node);
                const selectedProgramId = programNode.data.schoolProgramId;
                programIds = [selectedProgramId, ...programIds.filter((id) => id !== selectedProgramId)];
            }
            this.schoolService.setSchoolPrograms(programIds);
        });

        // this.$jsTreeDiv.on('changed.jstree', (e, data) => {
        //     const selectedNodes = jsTree.jstree().get_selected(true);
        //
        //     const programIds = []
        //
        //     for (let selectedNode of selectedNodes) {
        //         if (selectedNode.data.schoolProgramId) {
        //             programIds.push(parseInt(selectedNode.data.schoolProgramId))
        //         }
        //     }
        //     console.log(programIds)
        // })
        // this.$jsTreeDiv.jstree(true).open_all();
        // this.$jsTreeDiv.find('li[data-checkstate="checked"]').each( (i, el) => {
        //     this.$jsTreeDiv.jstree('check_node', $(el));
        // });
        // this.$jsTreeDiv.jstree(true).close_all();
        return res
    }
}

export class SwitchSchoolMenu extends Component {
    static template = 'edoob.SwitchSchoolMenu';
    static components = [SwitchSchoolTree];

    setup() {
        this.schoolService = useService("school");
        this.currentSchoolProgram = this.schoolService.currentSchoolProgram;
    }
}

QWeb.registerComponent("SwitchSchoolMenu", SwitchSchoolMenu);
QWeb.registerComponent("SwitchSchoolTree", SwitchSchoolTree);

registry.category("systray").add("edoob.SwitchSchoolMenu", {Component: SwitchSchoolMenu}, {sequence: 2});

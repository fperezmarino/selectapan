/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { session } from "@web/session";

function parseSchoolProgramIds(pidsFromHash) {
    const pids = [];
    if (pidsFromHash) {
        if (typeof pidsFromHash === "string") {
            pids.push(...pidsFromHash.split(",").map(Number));
        } else if (typeof pidsFromHash === "number") {
            pids.push(pidsFromHash);
        }
    }
    return pids;
}

function computeAllowedSchoolProgramValues(pids) {
    const user_programs_data = session.user_programs;
    const availableSchoolProgramFromSession = user_programs_data.allowed_programs;
    const allowedSchoolProgramIds = pids || [];
    let allowedSchoolProgramValuesList = []
    for (let pid of allowedSchoolProgramIds) {
        const allowedSchoolVals = _.find(availableSchoolProgramFromSession, pVals => pVals.id === pid);
        if (allowedSchoolVals) {
            allowedSchoolProgramValuesList.push(allowedSchoolVals);
        }
    }
    availableSchoolProgramFromSession.filter(pVals => allowedSchoolProgramIds.includes(pVals.id));

    const notReallyAllowedSchoolProgram = allowedSchoolProgramValuesList.filter(
        pVals => !(_.chain(availableSchoolProgramFromSession).pluck('id').contains(pVals.id).value())
    );

    if (user_programs_data.current_program.id && (!allowedSchoolProgramValuesList.length || notReallyAllowedSchoolProgram.length)) {
        allowedSchoolProgramValuesList = [user_programs_data.current_program];
    }
    return allowedSchoolProgramValuesList;
}

export const schoolService = {
    dependencies: ["user", "router", "cookie"],
    start(env, { user, router, cookie }) {
        let pids;
        if ("pids" in router.current.hash) {
            pids = parseSchoolProgramIds(router.current.hash.pids);
        } else if ("pids" in cookie.current) {
            pids = parseSchoolProgramIds(cookie.current.pids);
        }
        
        const allowedProgramValues = computeAllowedSchoolProgramValues(pids, 'program');
        const allowedProgramIds = _.pluck(allowedProgramValues, 'id');
        const stringPIds = allowedProgramIds.join(",");
        router.pushState({ pids: stringPIds }, { lock: false, replace: true });
        cookie.setCookie("pids", stringPIds);

        user.updateContext({ allowed_program_ids: allowedProgramIds });
        const availableSchoolPrograms = session.user_programs.allowed_programs;
        const availableSchools = session.user_schools.allowed_schools;
        const availableSchoolDistricts = session.user_districts.allowed_districts;


        return {
            availableSchoolPrograms,
            availableSchools,
            availableSchoolDistricts,

            get allowedProgramIds() {
                return allowedProgramIds.slice(0);
            },
            get currentSchoolProgram() {
                return allowedProgramValues && allowedProgramValues.length ? allowedProgramValues[0] : {}
            },

            setSchoolPrograms(programIds) {
                let nextSchoolProgramIds = programIds || []
                router.pushState({pids: nextSchoolProgramIds}, {lock: false, replace: true });
                cookie.setCookie("pids", nextSchoolProgramIds);
                browser.setTimeout(() => browser.location.reload()); // history.pushState is a little async
            },
        };
    },
};

registry.category("services").add("school", schoolService);
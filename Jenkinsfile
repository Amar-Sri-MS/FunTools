// FunOS, FunHW, qemu, FunTools and FunSDK-small
//
// This is a trigger jenkinsfile for PR plugin and
// is copied into above listed repos. So please update
// all the copies if you make, most unlikely event,
// any changes here.

// Load library from default or specified branch
if (env.BRANCH_FunJenkins) {
	library "FunJenkins@${env.BRANCH_FunJenkins}"
} else {
	library "FunJenkins"
}

funosPipeline()

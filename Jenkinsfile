//
// jenkins ci pipeline
// FunOS for FunSDKv2
//
//

// archive server/location for qemu image
ARCHIVE_SERVER = 'jenkins-archive'

// server location for output archiving
OUTPUT_ARCHIVE_DIR = '/project/users/doc/jenkins/funsdk'

// tag prefix
TAG_PREFIX = 'bld_'
TAG_BLD = "${TAG_PREFIX}${BUILD_NUMBER}"

// funos funcp on_demand
node ('funos') {
timestamps {

	try {

		parallel (
			build_local: {
				buildStages('funos')

				// early archive so to diagnose
				// dead builds
				stage('Archive') {
					archive()
				} // archive

				dir ('FunOS') {
					sh "time build/funos-posix"
				}
			}, // build_local
			build_mac: {
				node ('funos_mac') {
					buildStages('funos_mac')

					// early archive so to diagnose
					// dead builds
					stage('Archive') {
						archive()
					} // archive

					dir ('FunOS') {
						sh "time build/funos-posix"
					}
				}
			} // build_mac
		) // parallel

		// run all the tests locally after both builds
		stage('Test setup') {
			testSetup()
		} // setup

		stage('Test Run') {
			testRun()
		} // test

		stage('Coverage') {
			codeCoverage()
		}

		stage('Tag') {
			addTag()
		} // tag

	        if (env.BRANCH_NAME == "master") {
		   stage('latestify') {

			// rename the prelim
			sh "ssh ${ARCHIVE_SERVER} mv ${OUTPUT_ARCHIVE_DIR}/${BUILD_NUMBER}_prelim  ${OUTPUT_ARCHIVE_DIR}/${BUILD_NUMBER}"
			
			// set up latest (symlink)
			sh "ssh ${ARCHIVE_SERVER} rm -rf ${OUTPUT_ARCHIVE_DIR}/latest"
			sh "ssh ${ARCHIVE_SERVER} ln -s ${BUILD_NUMBER}  ${OUTPUT_ARCHIVE_DIR}/latest"

		   } // latestify
		} // master branch

		stage('Cleanup') {
			dir ('FunSDK') {
				sh "scripts/bob --clean -a"
			}
		}

	} catch (err) {

		currentBuild.result = "FAILED"

		sh 'env'
		sh 'ps -eo user,ppid,pid,pcpu,pmem,vsize,rssize,tname,stat,start_time,bsdtime,args'

		echo "FunOS build error is here: ${env.BUILD_URL} at server=${NODE_NAME}, workspace=${WORKSPACE}"

		throw err

	} finally {

		sh 'env'

		stage('log parse') {
			step([$class: 'LogParserPublisher',
				parsingRulesPath: '/var/lib/jenkins/jenkins-rule-logparser',
				useProjectRule: false])
		}

		echo "Clean up qemu_image workspace"
		// files are saved as root, and SW-612 to see if they are saved as non-root user
		sh 'sudo rm -rf qemu_image'
		sh 'sudo -E FunSDK/scripts/bob --clean-cache --sure -C ${WORKSPACE}/FunSDK-cache'

		passedBuilds = []
		lastSuccessfulBuild(passedBuilds, currentBuild);
		def changeLog = getChangeLog(passedBuilds)
		echo "changeLog:"
		echo "=========="
		echo "${changeLog}"

		// Success or failure, always send notifications
		notifyResult(currentBuild.result, changeLog)

	} // try/catch
} // timestamp
} // node

def buildStages(label) {
    stage('Check out') {
	checkoutRepo()
    } // checkoutRepo

    stage('clean workspace') {
    	cleanWorkspace()
    }

    echo "Doing build"

    stage('Build') {
	build(label)
    } // build
}

def doCheckout(wsdir, repo, branch) {
	def currentRepo = getCurrentRepo()

    dir (wsdir) {
	if ("${repo}" == "${currentRepo}") {
		// Use scm step for clone to allow pre-build merge
		// and update remote URL to ensure tag push works
		checkout scm
		sh "git remote set-url origin git@github.com:fungible-inc/${repo}.git"
	} else {
		// Use checkout step to clone, no pre-build merge
		checkout([$class: 'GitSCM',
				userRemoteConfigs: [[url: "git@github.com:fungible-inc/${repo}.git"]],
				branches: [[name: branch]],
				browser: [$class: 'GithubWeb',
				repoUrl: "https://github.com/fungible-inc/${repo}"],
				extensions: [
					[$class: 'CloneOption', shallow: true],
					[$class: 'CloneOption', timeout: 20],
					[$class: 'CheckoutOption', timeout: 20]
				],
		])
    }
	}
}

def getCurrentRepo() {
	// CHANGE_URL is "https://github.com/fungible-inc/<repo>/pull/<PR>"
	if (env.CHANGE_URL) {
		String change = env.CHANGE_URL
		String[] _segments = change.split("/")
		return _segments[4]
	}
	return ""
}

def checkoutRepo() {
	timeout(time: 30, unit: 'MINUTES') {
	
	String BRANCH_FUNSDK = "master"
	String BRANCH_FUNOS = "master"
	String BRANCH_SBPFW = "fungible/master"
	String BRANCH_QEMU = "f1"
	String BRANCH_ACCEL = "rajeshmohan/cryptoaccel"
	String BRANCH_FUNTOOLS = "master"
	String BRANCH_FUNHW = "master"
	String BRANCH_PDCLIBC = "master"
	String BRANCH_ACC_COMPRESSION = "master"
	String BRANCH_ACC_REGEX = "master"
	String BRANCH_AAPL = "master"
    String BRANCH_FUNCONTROLPLANE = "master"

	sh 'env'

	parallel (
		checkout_funos: {
		doCheckout('FunOS',
				'FunOS',
				"*/${BRANCH_FUNOS}")
		}, // checkout_funos
		checkout_sbpfw: {
		doCheckout('SBPFirmware',
				'SBPFirmware',
				"*/${BRANCH_SBPFW}")
		}, // checkout_sbpfw

		checkout_funsdk: {
		doCheckout('FunSDK',
				'FunSDK-small',
				"*/${BRANCH_FUNSDK}")
		}, // checkout_fusdk

		checkout_qemu: {
		doCheckout('qemu',
				'qemu',
				"*/${BRANCH_QEMU}")
		}, // checkout_qemu

		//checkout_funcp: {
		//	doCheckout('FunControlPlane',
		//		   'FunControlPlane',
		//		   '*/cgray/FunSDKv2')
		//}, // checkout_qemu

		checkout_accelerators: {
		doCheckout('Accelerators',
				'Accelerators',
				"*/${BRANCH_ACCEL}")
		}, // checkout_accelerators

		checkout_funtools: {
		doCheckout('FunTools',
				'FunTools',
				"*/${BRANCH_FUNTOOLS}")
		}, // checkout_funtools

		checkout_funhw: {
		doCheckout('FunHW',
				'FunHW',
				"*/${BRANCH_FUNHW}")
		}, // checkout_funhw

		checkout_pdclibc: {
		doCheckout('pdclibc',
				'pdclibc',
				"*/${BRANCH_PDCLIBC}")
		}, // checkout_pdclibc

		checkout_accel_compression: {
		doCheckout('accel-compression',
				'accel-compression',
				"*/${BRANCH_ACC_COMPRESSION}")
		}, // checkout_accel_compression

		checkout_accel_regex: {
			doCheckout('accel-regex',
				'accel-regex',
				"*/${BRANCH_ACC_REGEX}")
		}, // checkout_accel_regex

		checkout_aapl: {
		doCheckout('aapl',
				'aapl',
				"*/${BRANCH_AAPL}")
		}, // checkout_aapl

        checkout_funcp: {
        doCheckout('FunControlPlane',
                'FunControlPlane',
                "*/${BRANCH_FUNCONTROLPLANE}")
        }, // checkout_funcp

	)

	} // timeout
}

def cleanWorkspace() {
	// storage clean up
	dir ('FunSDK/integration_test') {
		// Run cleanup as root as a failed qemu based test could leave
		// behind files owned by root - SWOS-761
		sh '''
		sudo -E ./test_runner.py --test common/test_cleanup
		'''
	}
}

def build(label) {

    // where we put interim build pieces
    String SDK_BUILD_DIR = "${WORKSPACE}/build"

    // Run the FunOS build
    timeout(time: 30, unit: 'MINUTES') {

	echo 'building FunOS core MACHINE'

	env
	
	sh "cd FunSDK;git clean -fdx"
	sh "rm -rf ${SDK_BUILD_DIR}"
	sh "mkdir -p ${SDK_BUILD_DIR}"
			
	sh "FunSDK/scripts/bob --clean --all"

	sh "FunSDK/scripts/bob --build aapl  -P $SDK_BUILD_DIR"

	// build all these on the same command-line to minimise rebuilds
	// for makefiles that don't do deps right
	sh "FunSDK/scripts/bob --build -P ${SDK_BUILD_DIR} --including libc.mips64 funos.posixclient funos.posix-base libc.mips64 funos.mips64-base funos.mips64-base" 

	sh "FunSDK/scripts/bob --build qemu -P $SDK_BUILD_DIR"
	sh "FunSDK/scripts/bob --build dpcsh -P $SDK_BUILD_DIR"
	sh "FunSDK/scripts/bob --build csrsh -P $SDK_BUILD_DIR"

	sh "ls -ltr ${SDK_BUILD_DIR}/*.tgz"

	// only run on funos node (linux node)
	if (label == "funos") {
	   // can do three distinct invocations since we're not doing
	   // a tree-op
	   sh "FunSDK/scripts/bob --build funos.posix-extra  -P $SDK_BUILD_DIR"
	   sh "FunSDK/scripts/bob --build funos.mips64-extra -P $SDK_BUILD_DIR"
	   sh "FunSDK/scripts/bob --build funos.mips64-verif -P $SDK_BUILD_DIR"
	}

        //if (label == "funos") {
        //      dir ('FunControlPlane') {
        //           echo 'Build full  FunControlPlane'
        //           sh "time make -j 8"
        //      }
        //}

    }// timeout
}

def testSetup() {
	timeout(time: 5, unit: 'MINUTES') {

	echo "Test Env Setup stage"

	dir ("FunSDK/integration_test") {
		sh "lib/build_setup.py"
	}

	echo "Test Env Setup done."
	} // timeout

	// SWOS-90, funcp not able to clean up processes
	echo 'Running: clean any running processes before running running test'
	sh "./FunOS/scripts/build_test.sh -k"
}

def testRun() {
	// Run the FunOS build test
	timeout(time: 60, unit: 'MINUTES') {
	parallel (
		posix_test: {
			echo 'Running: posix x86 build test'
			sh "./FunOS/scripts/build_test.sh x86"
			sh "./FunOS/scripts/build_test.sh dpc"
			sh "./FunOS/scripts/build_test.sh ikv"
			echo 'Done: posix build test'
		},	// posix_test
		mips_test: {
			echo 'Running: mips build test'
			sh "./FunOS/scripts/build_test.sh mips-f1"
			echo 'Done: mips build test'
		}	// mips_test
	) // parallel

	} // timeout
	timeout(time: 25, unit: 'MINUTES') {
		timestamps {
			echo 'Running: host integration test'
			dir('FunSDK/integration_test') {
				sh "./test_runner.py --test host"
			}
		    echo 'Done: host integration test'
		} // timestamps
	} // timeout
	timeout(time: 15, unit: 'MINUTES') {
		timestamps {
			echo 'Running: L3 integration test'
			sh "sudo rm -f psim.log"
			dir('FunControlPlane') {
				// SWLINUX-89 disable temporarily
				// sh "./scripts/nutest/test_l3_traffic all "
			}
		    echo 'Done: L3 integration test'
		} // timestamps
	} // timeout
	echo "Test run done."
}

def codeCoverage() {
	timeout(time: 30, unit: 'MINUTES') {

	// all platform tests
	sh "./FunOS/build/funos-posix-cov app=test"
	sh "./FunOS/build/funos-posix-cov app=hu_test"

	// sh "./FunOS/build/funos-posix-cov app=hu_test_crypto"
	sh "./FunOS/build/funos-posix-cov app=crypto_test"

	//  SWOS-314
	//sh "./FunOS/build/funos-posix-cov app=flow_test --vpspin"
	sh "./FunOS/build/funos-posix-cov app=ec_test"

	sh "gcovr -r . --xml -o FunOS/build/coverage.xml"
	sh "gcovr -r . --html --html-details -o FunOS/build/coverage.html"

	step([$class: 'CoberturaPublisher', autoUpdateHealth: false,
	     autoUpdateStability: false, coberturaReportFile: 'FunOS/build/coverage.xml',
	     failUnhealthy: false, failUnstable: false, maxNumberOfBuilds: 0,
	     onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false])

	} // timeout
}

def addTag() {
	// FIXME move this to common script (FunSDK)

	if (!env.CHANGE_TARGET) {
		echo "adding tag ${TAG_BLD}"
		def date = new Date().format("yyyy/MM/dd/HH/mm")
		// NOTE: tag name should be revisited, such as rel_bld_1234..
		// tag format 'bld_1234'

		def _dirs = [ 'FunOS', 'FunSDK', 'qemu', 'FunTools', 'FunHW', 'pdclibc', 'SBPFirmware' ]

		_dirs.each() {
			dir ("${it}") {
				sh "git tag -a ${TAG_BLD} -m\"${TAG_BLD} ${date}\""
				sh "git push origin ${TAG_BLD}"
			}
		}

		echo "Tagging done."
	}

	// create build.txt
	// contains build number
	sh "echo ${BUILD_NUMBER} > build_info.txt"
	sh "cat build_info.txt"
}

def archive() {
	// FIXME move this to common script (FunSDK)
	// FIXME prepare a list of files and process them instead individual scp-ing

	String C = '-o "StrictHostKeyChecking no"'

	// where we put interim build pieces
    	String SDK_BUILD_DIR = "${WORKSPACE}/build"

	// where the projectdb.json is
	String PROJECTDB = "${WORKSPACE}/FunSDK/scripts/projectdb.json"

	if (fileExists(PROJECTDB)) {
	    sh 'echo projectdb.json exists'
	    sh "cat ${PROJECTDB}"
	} else {
	    sh 'echo projectdb.json is missing'
	}

	if (env.BRANCH_NAME == "master") {

		echo "archiving files"

		def BUILD_OS = sh(script: 'uname', returnStdout: true)
		echo "Build OS: ${BUILD_OS}"

		echo "preliminarily archiving files at ${OUTPUT_ARCHIVE_DIR}/${BUILD_NUMBER}_prelim/${BUILD_OS}"

		// set up build dir
		sh "ssh $C ${ARCHIVE_SERVER} mkdir -p ${OUTPUT_ARCHIVE_DIR}/${BUILD_NUMBER}_prelim/${BUILD_OS}" 

		// create build.txt
		// contains build number
		sh "echo ${BUILD_NUMBER} > ${SDK_BUILD_DIR}/build_info.txt"
		sh "cat ${SDK_BUILD_DIR}/build_info.txt"

		// scp build number to root
		sh "scp $C ${SDK_BUILD_DIR}/build_info.txt ${ARCHIVE_SERVER}:${OUTPUT_ARCHIVE_DIR}/${BUILD_NUMBER}_prelim"


		if (fileExists(PROJECTDB)) {
		    sh "scp $C ${PROJECTDB} ${ARCHIVE_SERVER}:${OUTPUT_ARCHIVE_DIR}/${BUILD_NUMBER}_prelim"
		}

		// scp files
		sh "scp $C ${SDK_BUILD_DIR}/*.tgz ${ARCHIVE_SERVER}:${OUTPUT_ARCHIVE_DIR}/${BUILD_NUMBER}_prelim/${BUILD_OS}"

		// add sha256 sum
		// FIXME
		// sh "ssh $C ${ARCHIVE_SERVER} \"cd ${OUTPUT_ARCHIVE_DIR}/${BUILD_NUMBER}_prelim; find . -type f -print0 | xargs -0 sha256sum > sha256sum\" "

		echo "Archiving done."
	}
}

def notifyResult(String buildStatus = 'STARTED', String changeLog) {

	// build status of null means successful
	buildStatus =  buildStatus ?: 'SUCCESSFUL'

	def change = env.CHANGE_URL
	def PROJECT = getCurrentRepo()
	def REPO_OWNER = getCurrentRepo()

	// if CHANGE_URL of null means PR merge to master
	change = change ?: 'PR merge'

	def subject = "${buildStatus}: Job ${PROJECT} (repo: ${REPO_OWNER}) ${env.BRANCH_NAME} build"
	def details = "FunOS (${env.BRANCH_NAME}) (${change})\n\r log is here: ${env.BUILD_URL}/flowGraphTable/\n\rserver=${NODE_NAME}\n\r workspace=${WORKSPACE}\n\r Last change:\n\r ${changeLog}"

	def sender = 'jenkins@fungible.com'
	def recipient = "${env.CHANGE_AUTHOR_EMAIL}"

	if (env.BRANCH_NAME == "master") {

		if (buildStatus == "SUCCESSFUL") {
			// no notfication on master build successful
			return
		}

		recipient = "sw@fungible.com"
	}

	mail (	to: recipient,
			from: sender,
			replyto: sender,
			subject: subject,
			body: details);

}

// from https://stackoverflow.com/questions/38084806/how-to-get-the-changes-since-the-last-successful-build-in-jenkins-pipeline

def lastSuccessfulBuild(passedBuilds, build) {
  if ((build != null) && (build.result != 'SUCCESS')) {
      passedBuilds.add(build)
      lastSuccessfulBuild(passedBuilds, build.getPreviousBuild())
   }
}

@NonCPS
def getChangeLog(passedBuilds) {
    def log = ""
    for (int x = 0; x < passedBuilds.size(); x++) {
        def currentBuild = passedBuilds[x];
        def changeLogSets = currentBuild.rawBuild.changeSets
        for (int i = 0; i < changeLogSets.size(); i++) {
            def entries = changeLogSets[i].items
            for (int j = 0; j < entries.length; j++) {
                def entry = entries[j]
                log += "* ${entry.msg} by ${entry.author} \n"
            }
        }
    }
    return log;
}


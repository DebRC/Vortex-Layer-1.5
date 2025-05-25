// SPDX-License-Identifier: GPL-3.0
/*
    Copyright 2021 0KIMS association.

    This file is generated with [snarkJS](https://github.com/iden3/snarkjs).

    snarkJS is a free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    snarkJS is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
    or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
    License for more details.

    You should have received a copy of the GNU General Public License
    along with snarkJS. If not, see <https://www.gnu.org/licenses/>.
*/

pragma solidity >=0.7.0 <0.9.0;

contract Groth16Verifier {
    // Scalar field size
    uint256 constant r    = 21888242871839275222246405745257275088548364400416034343698204186575808495617;
    // Base field size
    uint256 constant q   = 21888242871839275222246405745257275088696311157297823662689037894645226208583;

    // Verification Key data
    uint256 constant alphax  = 20456734148601039959522462607957008270119873842578813934203033199523421085399;
    uint256 constant alphay  = 7525507498607250008644652897782516488779144007516623827769024883051351227714;
    uint256 constant betax1  = 829054091500966284530084441562287540483628134675138106731991429038247969973;
    uint256 constant betax2  = 1281936605568318363600999138250386724422296158752810004625729300092310294198;
    uint256 constant betay1  = 21647917669045221177961249312355843810328043403216456778702489758464942236282;
    uint256 constant betay2  = 8601916184158524791806244600658371321142674108037435779042565081320863207499;
    uint256 constant gammax1 = 11559732032986387107991004021392285783925812861821192530917403151452391805634;
    uint256 constant gammax2 = 10857046999023057135944570762232829481370756359578518086990519993285655852781;
    uint256 constant gammay1 = 4082367875863433681332203403145435568316851327593401208105741076214120093531;
    uint256 constant gammay2 = 8495653923123431417604973247489272438418190587263600148770280649306958101930;
    uint256 constant deltax1 = 45767238157407116071804978273166925988714814989254884286572038270488525753;
    uint256 constant deltax2 = 66052637690579262244560734993325684420980259472815686323282074561175672430;
    uint256 constant deltay1 = 4144896606991306313845596702072254769472414049144785989911836529573630714480;
    uint256 constant deltay2 = 15467087097011577258480708574564821293117224689037950554921557363774888626688;

    
    uint256 constant IC0x = 1467456883699954467121447475087971469477543817958535192127566193858023449280;
    uint256 constant IC0y = 16165579852934997014192392650867030216195329423394544481230134780396188998781;
    
    uint256 constant IC1x = 21111897282727229484746035827970093122675019584905919729634761676266567050398;
    uint256 constant IC1y = 13585189444168608159755101049343180133318305065314815047375991728052024681534;
    
    uint256 constant IC2x = 16085405082862738829283735179782863929779797139327021356153540158740661774274;
    uint256 constant IC2y = 10878632702765492942247266035928120535471921768117766668828018088195501550063;
    
    uint256 constant IC3x = 16262846595037469115352882701692419208805581337129354958070837848786946410937;
    uint256 constant IC3y = 8882637961636092562489518021541030670993606577981110518895869108581890275955;
    
    uint256 constant IC4x = 4492163037037168915008132948328130349322507962185996324296824824837633775755;
    uint256 constant IC4y = 15050067288132208539051025803109814190690561097379182645518299848656952105473;
    
    uint256 constant IC5x = 5250985588139727532489032559132046797833392237251061273985670013299950695866;
    uint256 constant IC5y = 9792950572527976712564513039423889940301985559437229363562135110244376326282;
    
    uint256 constant IC6x = 16852606457885252510300895613889273741316253212674538905573298261049684042355;
    uint256 constant IC6y = 12094961213164892505724838229375079832010392092233637087871576852560503600421;
    
    uint256 constant IC7x = 13776959599631683648123550148085354812759605391232599680723561537021543425283;
    uint256 constant IC7y = 20267680396156206930584762786364215359368123490127057506210172310096783493538;
    
    uint256 constant IC8x = 20139375825065212329578689483385223435667607580362800502086654872094143106994;
    uint256 constant IC8y = 20679995179101968967598238845332963658964498578990996664833884343201966220339;
    
    uint256 constant IC9x = 15794133561717786107990260101099196995402649794291992183004796441664548547217;
    uint256 constant IC9y = 15497092051874035745444741814409126233172495676875219329732987747090736275862;
    
    uint256 constant IC10x = 15873719182365673860878177436701058135214166202554634097352081106338609763293;
    uint256 constant IC10y = 7022381296412420487459596076228095456900488856921528899531019527504215764786;
    
    uint256 constant IC11x = 10385138079255028929964633140910071721495544633812196668325683549106272204097;
    uint256 constant IC11y = 18441744766396987512361252445537740945896694592569524213000619145609472342784;
    
    uint256 constant IC12x = 19828434214074632307890541288168830767285810344363981105081958232657794678778;
    uint256 constant IC12y = 1609936285172221206757715240128375328178198769020541869151210822779888777619;
    
    uint256 constant IC13x = 17071840051725984471451516673621244155465993058135518360950576118674121946210;
    uint256 constant IC13y = 390048872211443282160105788028825313620821865152125507489401250498677548531;
    
    uint256 constant IC14x = 7058384976908725669276677093122461747811349769729897812834965309244040395202;
    uint256 constant IC14y = 223728339060272093936184508361165000351270179775829395710594095606970032544;
    
    uint256 constant IC15x = 6049657406653645958257024422148511381909791823403114205081813315786366392811;
    uint256 constant IC15y = 16436738431916508539798956943010206522465370940950682851793819575398064859042;
    
    uint256 constant IC16x = 4312596306285677070008942361077105711571781623596769059281228612863631926658;
    uint256 constant IC16y = 21112032612021258874906899755254302076585558545972087783561712061952262267626;
    
    uint256 constant IC17x = 9792587285719298592286312189805183963884303167807113327882469031583496734948;
    uint256 constant IC17y = 20241888718918202525516609765283151098007674986291790274798187576695719764634;
    
    uint256 constant IC18x = 20206803255434285780413993427901326124577613083014029290257575217929159950078;
    uint256 constant IC18y = 10457903311117986463147923009931747060691745190793088743005226717665638439530;
    
    uint256 constant IC19x = 6251857977388541480709005024658832602413053045488372964434365609590860185129;
    uint256 constant IC19y = 14766595239610379436390891354815805703767883030397532935859564995130359304490;
    
    uint256 constant IC20x = 12315688804829585663859371452518412943036817762309321024285770946241848318085;
    uint256 constant IC20y = 18955505948794045110212831215355438878609928557092898971130619139193090601566;
    
    uint256 constant IC21x = 13922450300171637167988979976053896560999257412858235665155870940193847702659;
    uint256 constant IC21y = 21238026744059071871551059809604317960052297573249813836336546985703857237198;
    
    uint256 constant IC22x = 19811772542565856867302984302299709257234428902495390943849639089429701479727;
    uint256 constant IC22y = 15099806879705606370135347762629489589087821694719770486616640920131887566471;
    
    uint256 constant IC23x = 20500933634773216608681225957647415231814797689105084549918802930803080530512;
    uint256 constant IC23y = 19342260437592160096227907728757798199003254929159603751354106235152802048690;
    
    uint256 constant IC24x = 10456530315634888891807529902692501309018921503852452786377967489312170545992;
    uint256 constant IC24y = 220940965951993214339309989931376103340503271590700357685994302354187181332;
    
    uint256 constant IC25x = 8409132680115972821714427517576826347946251205009862237544285666360602497924;
    uint256 constant IC25y = 6878790503887515062736696525598591838276773706178351510175410997053481322275;
    
    uint256 constant IC26x = 19889273708741113853663029550529956366830518082568900484320507389422774943871;
    uint256 constant IC26y = 7286154489813212041080802928845032340534742122088543772397723767578357989301;
    
    uint256 constant IC27x = 18901428053909287633964143201572523282314993426837742654226045509667706049723;
    uint256 constant IC27y = 1745529554588812738484990803517951010113890658039927105243634638595097160076;
    
    uint256 constant IC28x = 12526071810599668761264696393203698016425527023591979748385076974371922165141;
    uint256 constant IC28y = 19802203536871350516501069586162935283333440489322774724429124418637525235183;
    
    uint256 constant IC29x = 21129747916559229609260751446447150789586809466481736058074126951227820712952;
    uint256 constant IC29y = 16040833472699187308253077379490947264887572712471437419322400569528556718207;
    
    uint256 constant IC30x = 9238735036815296235753996037414677982691681535023313008910623899185000698252;
    uint256 constant IC30y = 466941681317136832039551391079866055568894062074830095033600125676203533905;
    
    uint256 constant IC31x = 17814590937626726305507499356075055607574676156118588312807028519609124198287;
    uint256 constant IC31y = 8904450990874878795135865190050486092908024617948017478406011740754022264474;
    
    uint256 constant IC32x = 15127384940528455875015879002965266450617453614695456214373043800216032410006;
    uint256 constant IC32y = 10782473392523368400687458706387609798585619118289736216727434248640578885605;
    
    uint256 constant IC33x = 6059611395499550302023492128026950447324303529897703305698949018570670855068;
    uint256 constant IC33y = 1114429611577851479136157018549904452029813537903340016940529857949176167036;
    
    uint256 constant IC34x = 18831890928307331067316461131976413382117611497011465934291079670703560643256;
    uint256 constant IC34y = 3397908594918794425752634145896163587474914032568600498826941152124169657972;
    
    uint256 constant IC35x = 4063275866188819783617889324135817715642690729293852173838790300806957646672;
    uint256 constant IC35y = 14073014179835375180273031085650063106956854343042077491547031310125454759344;
    
    uint256 constant IC36x = 3724209152988340171568360741525851757427692905087071967990705192547081451848;
    uint256 constant IC36y = 4488079912196278597279607297982110950162744526612378449682605069069875824280;
    
    uint256 constant IC37x = 694647440346738056606702858608840798933423898548394351290733147091056903162;
    uint256 constant IC37y = 20376910441351454302022435724639255674946631275776644455979581490127620604726;
    
    uint256 constant IC38x = 9215393351087892760325434128657538991848482344719555593551387174968424655868;
    uint256 constant IC38y = 6204720555539876129344645482955590430435177480879331225241101752821708460743;
    
    uint256 constant IC39x = 2377860107535321882310309774612953167265355498202215918498264653815772721858;
    uint256 constant IC39y = 18856284337868299506470161338884094732837062115446287081130997313437596562295;
    
    uint256 constant IC40x = 18914281890580447626783637008223556582834738018763072833557281293451931202764;
    uint256 constant IC40y = 11523899090864235410182692710530321426606566181223035081194840661587782125432;
    
 
    // Memory data
    uint16 constant pVk = 0;
    uint16 constant pPairing = 128;

    uint16 constant pLastMem = 896;

    function verifyProof(uint[2] calldata _pA, uint[2][2] calldata _pB, uint[2] calldata _pC, uint[40] calldata _pubSignals) public view returns (bool) {
        assembly {
            function checkField(v) {
                if iszero(lt(v, r)) {
                    mstore(0, 0)
                    return(0, 0x20)
                }
            }
            
            // G1 function to multiply a G1 value(x,y) to value in an address
            function g1_mulAccC(pR, x, y, s) {
                let success
                let mIn := mload(0x40)
                mstore(mIn, x)
                mstore(add(mIn, 32), y)
                mstore(add(mIn, 64), s)

                success := staticcall(sub(gas(), 2000), 7, mIn, 96, mIn, 64)

                if iszero(success) {
                    mstore(0, 0)
                    return(0, 0x20)
                }

                mstore(add(mIn, 64), mload(pR))
                mstore(add(mIn, 96), mload(add(pR, 32)))

                success := staticcall(sub(gas(), 2000), 6, mIn, 128, pR, 64)

                if iszero(success) {
                    mstore(0, 0)
                    return(0, 0x20)
                }
            }

            function checkPairing(pA, pB, pC, pubSignals, pMem) -> isOk {
                let _pPairing := add(pMem, pPairing)
                let _pVk := add(pMem, pVk)

                mstore(_pVk, IC0x)
                mstore(add(_pVk, 32), IC0y)

                // Compute the linear combination vk_x
                
                g1_mulAccC(_pVk, IC1x, IC1y, calldataload(add(pubSignals, 0)))
                
                g1_mulAccC(_pVk, IC2x, IC2y, calldataload(add(pubSignals, 32)))
                
                g1_mulAccC(_pVk, IC3x, IC3y, calldataload(add(pubSignals, 64)))
                
                g1_mulAccC(_pVk, IC4x, IC4y, calldataload(add(pubSignals, 96)))
                
                g1_mulAccC(_pVk, IC5x, IC5y, calldataload(add(pubSignals, 128)))
                
                g1_mulAccC(_pVk, IC6x, IC6y, calldataload(add(pubSignals, 160)))
                
                g1_mulAccC(_pVk, IC7x, IC7y, calldataload(add(pubSignals, 192)))
                
                g1_mulAccC(_pVk, IC8x, IC8y, calldataload(add(pubSignals, 224)))
                
                g1_mulAccC(_pVk, IC9x, IC9y, calldataload(add(pubSignals, 256)))
                
                g1_mulAccC(_pVk, IC10x, IC10y, calldataload(add(pubSignals, 288)))
                
                g1_mulAccC(_pVk, IC11x, IC11y, calldataload(add(pubSignals, 320)))
                
                g1_mulAccC(_pVk, IC12x, IC12y, calldataload(add(pubSignals, 352)))
                
                g1_mulAccC(_pVk, IC13x, IC13y, calldataload(add(pubSignals, 384)))
                
                g1_mulAccC(_pVk, IC14x, IC14y, calldataload(add(pubSignals, 416)))
                
                g1_mulAccC(_pVk, IC15x, IC15y, calldataload(add(pubSignals, 448)))
                
                g1_mulAccC(_pVk, IC16x, IC16y, calldataload(add(pubSignals, 480)))
                
                g1_mulAccC(_pVk, IC17x, IC17y, calldataload(add(pubSignals, 512)))
                
                g1_mulAccC(_pVk, IC18x, IC18y, calldataload(add(pubSignals, 544)))
                
                g1_mulAccC(_pVk, IC19x, IC19y, calldataload(add(pubSignals, 576)))
                
                g1_mulAccC(_pVk, IC20x, IC20y, calldataload(add(pubSignals, 608)))
                
                g1_mulAccC(_pVk, IC21x, IC21y, calldataload(add(pubSignals, 640)))
                
                g1_mulAccC(_pVk, IC22x, IC22y, calldataload(add(pubSignals, 672)))
                
                g1_mulAccC(_pVk, IC23x, IC23y, calldataload(add(pubSignals, 704)))
                
                g1_mulAccC(_pVk, IC24x, IC24y, calldataload(add(pubSignals, 736)))
                
                g1_mulAccC(_pVk, IC25x, IC25y, calldataload(add(pubSignals, 768)))
                
                g1_mulAccC(_pVk, IC26x, IC26y, calldataload(add(pubSignals, 800)))
                
                g1_mulAccC(_pVk, IC27x, IC27y, calldataload(add(pubSignals, 832)))
                
                g1_mulAccC(_pVk, IC28x, IC28y, calldataload(add(pubSignals, 864)))
                
                g1_mulAccC(_pVk, IC29x, IC29y, calldataload(add(pubSignals, 896)))
                
                g1_mulAccC(_pVk, IC30x, IC30y, calldataload(add(pubSignals, 928)))
                
                g1_mulAccC(_pVk, IC31x, IC31y, calldataload(add(pubSignals, 960)))
                
                g1_mulAccC(_pVk, IC32x, IC32y, calldataload(add(pubSignals, 992)))
                
                g1_mulAccC(_pVk, IC33x, IC33y, calldataload(add(pubSignals, 1024)))
                
                g1_mulAccC(_pVk, IC34x, IC34y, calldataload(add(pubSignals, 1056)))
                
                g1_mulAccC(_pVk, IC35x, IC35y, calldataload(add(pubSignals, 1088)))
                
                g1_mulAccC(_pVk, IC36x, IC36y, calldataload(add(pubSignals, 1120)))
                
                g1_mulAccC(_pVk, IC37x, IC37y, calldataload(add(pubSignals, 1152)))
                
                g1_mulAccC(_pVk, IC38x, IC38y, calldataload(add(pubSignals, 1184)))
                
                g1_mulAccC(_pVk, IC39x, IC39y, calldataload(add(pubSignals, 1216)))
                
                g1_mulAccC(_pVk, IC40x, IC40y, calldataload(add(pubSignals, 1248)))
                

                // -A
                mstore(_pPairing, calldataload(pA))
                mstore(add(_pPairing, 32), mod(sub(q, calldataload(add(pA, 32))), q))

                // B
                mstore(add(_pPairing, 64), calldataload(pB))
                mstore(add(_pPairing, 96), calldataload(add(pB, 32)))
                mstore(add(_pPairing, 128), calldataload(add(pB, 64)))
                mstore(add(_pPairing, 160), calldataload(add(pB, 96)))

                // alpha1
                mstore(add(_pPairing, 192), alphax)
                mstore(add(_pPairing, 224), alphay)

                // beta2
                mstore(add(_pPairing, 256), betax1)
                mstore(add(_pPairing, 288), betax2)
                mstore(add(_pPairing, 320), betay1)
                mstore(add(_pPairing, 352), betay2)

                // vk_x
                mstore(add(_pPairing, 384), mload(add(pMem, pVk)))
                mstore(add(_pPairing, 416), mload(add(pMem, add(pVk, 32))))


                // gamma2
                mstore(add(_pPairing, 448), gammax1)
                mstore(add(_pPairing, 480), gammax2)
                mstore(add(_pPairing, 512), gammay1)
                mstore(add(_pPairing, 544), gammay2)

                // C
                mstore(add(_pPairing, 576), calldataload(pC))
                mstore(add(_pPairing, 608), calldataload(add(pC, 32)))

                // delta2
                mstore(add(_pPairing, 640), deltax1)
                mstore(add(_pPairing, 672), deltax2)
                mstore(add(_pPairing, 704), deltay1)
                mstore(add(_pPairing, 736), deltay2)


                let success := staticcall(sub(gas(), 2000), 8, _pPairing, 768, _pPairing, 0x20)

                isOk := and(success, mload(_pPairing))
            }

            let pMem := mload(0x40)
            mstore(0x40, add(pMem, pLastMem))

            // Validate that all evaluations ∈ F
            
            checkField(calldataload(add(_pubSignals, 0)))
            
            checkField(calldataload(add(_pubSignals, 32)))
            
            checkField(calldataload(add(_pubSignals, 64)))
            
            checkField(calldataload(add(_pubSignals, 96)))
            
            checkField(calldataload(add(_pubSignals, 128)))
            
            checkField(calldataload(add(_pubSignals, 160)))
            
            checkField(calldataload(add(_pubSignals, 192)))
            
            checkField(calldataload(add(_pubSignals, 224)))
            
            checkField(calldataload(add(_pubSignals, 256)))
            
            checkField(calldataload(add(_pubSignals, 288)))
            
            checkField(calldataload(add(_pubSignals, 320)))
            
            checkField(calldataload(add(_pubSignals, 352)))
            
            checkField(calldataload(add(_pubSignals, 384)))
            
            checkField(calldataload(add(_pubSignals, 416)))
            
            checkField(calldataload(add(_pubSignals, 448)))
            
            checkField(calldataload(add(_pubSignals, 480)))
            
            checkField(calldataload(add(_pubSignals, 512)))
            
            checkField(calldataload(add(_pubSignals, 544)))
            
            checkField(calldataload(add(_pubSignals, 576)))
            
            checkField(calldataload(add(_pubSignals, 608)))
            
            checkField(calldataload(add(_pubSignals, 640)))
            
            checkField(calldataload(add(_pubSignals, 672)))
            
            checkField(calldataload(add(_pubSignals, 704)))
            
            checkField(calldataload(add(_pubSignals, 736)))
            
            checkField(calldataload(add(_pubSignals, 768)))
            
            checkField(calldataload(add(_pubSignals, 800)))
            
            checkField(calldataload(add(_pubSignals, 832)))
            
            checkField(calldataload(add(_pubSignals, 864)))
            
            checkField(calldataload(add(_pubSignals, 896)))
            
            checkField(calldataload(add(_pubSignals, 928)))
            
            checkField(calldataload(add(_pubSignals, 960)))
            
            checkField(calldataload(add(_pubSignals, 992)))
            
            checkField(calldataload(add(_pubSignals, 1024)))
            
            checkField(calldataload(add(_pubSignals, 1056)))
            
            checkField(calldataload(add(_pubSignals, 1088)))
            
            checkField(calldataload(add(_pubSignals, 1120)))
            
            checkField(calldataload(add(_pubSignals, 1152)))
            
            checkField(calldataload(add(_pubSignals, 1184)))
            
            checkField(calldataload(add(_pubSignals, 1216)))
            
            checkField(calldataload(add(_pubSignals, 1248)))
            

            // Validate all evaluations
            let isValid := checkPairing(_pA, _pB, _pC, _pubSignals, pMem)

            mstore(0, isValid)
             return(0, 0x20)
         }
     }
 }

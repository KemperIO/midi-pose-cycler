## Form Table

| Form label              | value                       |
|-------------------------|------------------------------|
| actionNameToCreate      | integration-test-04         |
| bpm                     | 96                          |
| beatsPerBar             | 4                           |
| blendFileToOutputAction | headless_test/actions.blend   |
| poseBlendFile           | assets/dobby-poses.blend           |
| midiFile                | assets/eight-bars-thang.mid |


## Video table
| Form label         | value                       |
|--------------------+-----------------------------|
| shouldCreateVideo? | yes                         |
| audioFile          | assets/eight-bars-thang.m4a |
| renderDir          | renders/                    |
| charFile           | assets/dobby-poses.blend    |

## Dance Table

| poseCatalog | track  | cycle mode   | interpolation | preHold | postHold |
|-------------|--------|--------------|---------------|---------|----------|
| hips        | shaker | random       | back          | 2       | 5        |
| feet        | horns  | loop         | quartic       |         |          |
| hands       | quack  | pitch_follow | quartic       |         | 3        |
